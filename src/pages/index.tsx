import {useState, useCallback} from 'react';
import Head from 'next/head';
import {styled} from 'baseui';
import {Header} from '../components/header';
import {RestaurantsView} from '../components/restaurants-view';
import {ChatView} from '../components/chat-view';
import {AboutModal} from '../components/about-modal';

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
}

export type Document = {
  text: string;
  name: string;
} | null;

const Index = () => {
  const [uploadModalIsOpen, setUploadModalIsOpen] = useState(false);
  const [aboutModalIsOpen, setAboutModalIsOpen] = useState(false);
  const [activeDocument, setActiveDocument] = useState<Document>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [highlightedText, setHighlightedText] = useState<string | null>(null);
  const [restoRecs, setRestoRecs] = useState<RestoRec[]>([]);

  const sendQuery = useCallback(async () => {
    if (!restoRecs) {
      return;
    }
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
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-type': 'application/json'
      },
      body: JSON.stringify({
        "description": input,
      }),
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
        };
        return restoRec;
      });
      setRestoRecs(responseRestoRecs);
    }
    setMessages((prev) => [
      ...prev.slice(0, prev.length - 1),
      {role: 'assistant', content: responseJson.pitch},
    ]);
  }, [input, restoRecs]);

  return (
    <Page>
      <Head>
        <title>CHOMPT</title>
      </Head>
      <AboutModal isOpen={aboutModalIsOpen} setIsOpen={setAboutModalIsOpen} />
      <Header
        setRestoRecs={setRestoRecs}
        setAboutModalIsOpen={setAboutModalIsOpen}
        setMessages={setMessages}
      />
      <Container>
        <RestaurantsView
          restoRecs={restoRecs}
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



// Place holder UI restos
// [
//   {
//     restoName: "Mr. Unlimited", 
//     review: "Serves the best Dangerwiches. Best part is the man just won't stop SLINGING touchdowns. It's incredible. But wait I forgot.... shhhhhh.... it's spppiiicccyyyyy....",
//     perfectFor: "Dangerwich",
//     priceRange: "$$$$$$$",
//     imageUrl: 'https://res.cloudinary.com/the-infatuation/image/upload/q_auto,f_auto/images/NYC_Roscioli_Group_AlexStaniloff-3_rcj3ub',
//     // image: 'https://phantom-marca.unidadeditorial.es/94ab73711619b8595a59c7a92786f0a6/resize/1320/f/webp/assets/multimedia/imagenes/2022/10/21/16663054271574.jpg'
//   },
//   {
//     restoName: "Arty's Chinese Pancakes", 
//     review: "Best in the fucking game!!!! Could eat a million of these. Truly unbelievable. Shoutout Mom",
//     perfectFor: "Eating your face off",
//     priceRange: "$",
//     imageUrl: 'https://emojis.wiki/thumbs/emojis/fuel-pump.webp'
//   },
//   {
//     restoName: "Broncos Country! Let's Ride!", 
//     review: "Kinda weird... this guy inside would not stop yelling Broncos Country!!! Let's ride.... He said it at least 35 times",
//     perfectFor: "Broncos Country",
//     priceRange: "$$$",
//     imageUrl: 'https://media.tenor.com/FKYPddIiP-oAAAAd/lets-ride-broncos.gif'
//   }
// ]