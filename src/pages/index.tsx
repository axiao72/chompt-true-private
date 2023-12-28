import {useState, useCallback} from 'react';
import Head from 'next/head';
import {styled} from 'baseui';
import {Header} from '../components/header';
import {RestaurantsView} from '../components/restaurants-view';
import {ChatView} from '../components/chat-view';
import {AboutModal} from '../components/about-modal';
import {ResModal} from '../components/res-modal';

const Page = styled('div', ({$theme}) => ({
  position: 'absolute',
  background: $theme.colors.backgroundPrimary,
  height: '100%',
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  overflow: 'auto',
}));

export const NAV_HEIGHT = 53;
const Container = styled('div', ({$theme}) => ({
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  background: $theme.colors.borderOpaque,
  gap: '1px',
  height: `calc(100% - ${NAV_HEIGHT}px)`,
}));

export type Message = {
  role: 'user' | 'assistant';
  content: string | null;
  isLoading?: boolean;
};

export type RestoRec = {
  restoName: string;
  review: string;
  perfectFor: string;
  priceRange: string;
  imageUrl ? : string;
  websiteUrl : string;
  nbrhood : string;
  resyUrl ? : string;
}

export type Document = {
  text: string;
  name: string;
} | null;

export type ReservationCriteria = {
  date: string;
  time: string;
  partySize: number;
} | null;

const Index = () => {
  const [uploadModalIsOpen, setUploadModalIsOpen] = useState(false);
  const [aboutModalIsOpen, setAboutModalIsOpen] = useState(false);
  const [activeDocument, setActiveDocument] = useState<Document>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [highlightedText, setHighlightedText] = useState<string | null>(null);
  const [restoRecs, setRestoRecs] = useState<RestoRec[]>([]);
  const [resMode, setResMode] = useState<boolean>(false);
  const [resModalIsOpen, setResModalIsOpen] = useState(false);
  // Set the defaults to today's date and a time!
  // const currentDate = new Date();
  // const [resDate, setResDate] = useState(currentDate);
  // const [resTime, setResTime] = useState(null);
  // const [resPartySize, setResPartySize] = useState(null);
  const [resCriteria, setResCriteria] = useState<ReservationCriteria>(null);
  const [usedReservations, setUsedReservations] = useState(true);

  const sendQuery = useCallback(async () => {
    if (!restoRecs) {
      return;
    }
    setUsedReservations(true);
    setInput('');
    setMessages((prev) => [
      ...prev,
      {role: 'user', content: input},
      {
        role: 'assistant',
        content: null,
        isLoading: true,
      },
    ]);
    console.log(input)
    // console.log('Date: ', resCriteria.date)
    // console.log('Time: ', resCriteria.time)
    // console.log('Party Size: ', resCriteria.partySize)  
    console.log('Reservation Criteria: ', resCriteria)
    let idealMealData = {}
    // If Reservation Mode is on, add the criteria to request payload object
    if (resMode) {
      idealMealData = {
        "description": input,
        "res_mode_on": resMode,
        "res_date": resCriteria.date,
        "res_time": resCriteria.time,
        "party_size": resCriteria.partySize
      };
    }
    // Otherwise, don't include those field (they're optional on the FastAPI side)
    else {
      idealMealData = {
        "description": input,
        "res_mode_on": resMode
      };
    }
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-type': 'application/json'
      },
      body: JSON.stringify(idealMealData),
    });

    const responseJson = await response.json();
    const responseRestos = responseJson.restos;

    if (responseRestos.length > 0) {
      const responseRestoRecs: RestoRec[] = responseRestos.map((resto) => {
        const restoRec: RestoRec = {
          restoName: resto.resto_name,
          review: resto.review,
          perfectFor: resto.perfect_for,
          priceRange: resto.price_range,
          imageUrl: resto.image_url,
          websiteUrl: resto.website,
          nbrhood: resto.neighborhood,
          resyUrl: resto.resy_url
        };
        return restoRec;
      });
      setRestoRecs(responseRestoRecs);
    }
    setMessages((prev) => [
      ...prev.slice(0, prev.length - 1),
      {role: 'assistant', content: responseJson.pitch},
    ]);
    setUsedReservations(responseJson.usedReservations);
    console.log(usedReservations);
  }, [input, restoRecs]);

  return (
    <Page>
      <Head>
        <title>CHOMPT</title>
      </Head>
      <AboutModal isOpen={aboutModalIsOpen} setIsOpen={setAboutModalIsOpen} />
      <ResModal
        isOpen={resModalIsOpen}
        setIsOpen={setResModalIsOpen}
        resMode={resMode}
        setResMode={setResMode}
        resCriteria={resCriteria}
        setResCriteria={setResCriteria}
      >
      </ResModal>
      <Header
        setRestoRecs={setRestoRecs}
        setAboutModalIsOpen={setAboutModalIsOpen}
        setMessages={setMessages}
      />
      <Container>
        <RestaurantsView
          restoRecs={restoRecs}
          resMode={resMode}
          resModalIsOpen={resModalIsOpen}
          setResMode={setResMode}
          setResModalIsOpen={setResModalIsOpen}
          usedReservations={usedReservations}
        />
        <ChatView
          messages={messages}
          input={input}
          setInput={setInput}
          sendQuery={sendQuery}
          restoRecs={restoRecs}
        />
      </Container>
    </Page>
  );
};

export default Index;