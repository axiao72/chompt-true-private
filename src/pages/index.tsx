import {useState, useCallback, useEffect} from 'react';
import Head from 'next/head';
import {styled} from 'baseui';
import {Header} from '../components/header';
import {RestaurantsView} from '../components/restaurants-view';
import {ChatView} from '../components/chat-view';
import {AboutModal} from '../components/about-modal';
import {PrimerModal} from '../components/primer-modal';
import {LoginModal} from '../components/login-modal';
import {SignupModal} from '../components/signup-modal';
import {ResModal} from '../components/res-modal';
import {CityModal} from '../components/city-modal';
import {
  Tabs,
  Tab,
  FILL,
  StyledTabList,
  StyledTabPanel,
} from 'baseui/tabs-motion';
import {Grid, Cell} from 'baseui/layout-grid';

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
  // gridTemplateColumns: '1fr',
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

export type User = {
  username: string;
  firstName: string;
  lastName: string;
}


const Index = () => {
  const [aboutModalIsOpen, setAboutModalIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [restoRecs, setRestoRecs] = useState<RestoRec[]>([]);
  const [resMode, setResMode] = useState<boolean>(false);
  const [resModalIsOpen, setResModalIsOpen] = useState(false);
  const [resModeToggleColor, setResModeToggleColor] = useState('#FFFFFF');
  const [loginModalIsOpen, setLoginModalIsOpen] = useState(false);
  const [signupModalIsOpen, setSignupModalIsOpen] = useState(false);
  const [primerModalIsOpen, setPrimerModalIsOpen] = useState(false);
  const [cityModalIsOpen, setCityModalIsOpen] = useState(false);
  // Set the defaults to today's date and a time!
  // const currentDate = new Date();
  const [resCriteria, setResCriteria] = useState<ReservationCriteria>(null);
  const [usedReservations, setUsedReservations] = useState(true);
  const [usedBoth, setUsedBoth] = useState(true);
  const [usedNeighborhood, setUsedNeighborhood] = useState(true);
  const [usedCuisine, setUsedCuisine] = useState(true);
  const [activeUser, setActiveUser] = useState<User>(null);
  const [activeKey, setActiveKey] = useState<React.Key>(0);
  const [chatIsLoading, setChatIsLoading] = useState(false);
  const [userCoordinates, setUserCoordinates] = useState(null);
  const [userCity, setUserCity] = useState('New York');

  const getUser = async (username) => {
    console.log("Getting user from cookies: ", username);
    // Log user in using username and password
    const response = await fetch(`/api/get_mongo_user/${username}`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }
    });
    const responseJson = await response.json();
    if (responseJson.success) {
        const loggedInUser: User = {
            username: responseJson.username,
            firstName: responseJson.firstName,
            lastName: responseJson.lastName
        };
        console.log(loggedInUser.username);
        setActiveUser(loggedInUser);
    }
    else {
        console.log(responseJson.error);
    }
};

  // const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  // console.log(isMobile ? 'Mobile' : 'Desktop');

  // On initial render:
  // Get username from cookies and get User from Mongo
  // Open primer modal
  useEffect(() => {
    // Get username from cookies if available
    if (typeof window !== 'undefined') {
      const cookie_username = document.cookie.replace(/(?:(?:^|.*;\s*)chompt_username\s*\=\s*([^;]*).*$)|^.*$/, "$1");
      console.log('Cookie Username: ', cookie_username, ' !!!');
      if (cookie_username !== '') {
        getUser(cookie_username);
      }
      else {
        console.log('No username in cookies :(');
      }
    }

    // Get user's location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          // Success callback
          const { latitude, longitude } = position.coords;
          setUserCoordinates({latitude, longitude});
          console.log('Got coordinates from browser: ', latitude, ' ', longitude);

          // Use latitude and longitude to get city location through OpenCage
          // const opencageApiKey = process.env.REACT_APP_OPENCAGE_API_KEY;
          const opencageApiKey = '615ffe469cda4821adb01bd362b5692e';
          const opencageApiUrl = `https://api.opencagedata.com/geocode/v1/json?q=${latitude}+${longitude}&key=${opencageApiKey}`;

          try {
            const opencageResponse = await fetch(opencageApiUrl);
            const cityData = await opencageResponse.json();

            if (cityData.results && cityData.results.length > 0) {
              const city = cityData.results[0].components.city;
              setUserCity(city);
              console.log('Opencage got city: ', city);
            }
          } catch (error) {
            console.error('Error getting city from coordinates using OpenCage: ', error.message);
          }
          
        },
        (error) => {
          // Error callback
          console.error('Error getting user location:', error.message);
        }
      );
    } else {
      console.error("Geolocation is not supported by user's browser");
    }

    // Open primer modal to give user rundown if not already an active user
    if (activeUser === null) {
      setPrimerModalIsOpen(true)
    }
  }, []);

  console.log(`User coordinates set to: ${userCoordinates}`);
  console.log(`User city set to: ${userCity}`);

  const sendQuery = useCallback(async () => {
    if (!restoRecs) {
      return;
    }
    setChatIsLoading(true);
    setUsedReservations(true);
    setUsedBoth(true);
    setUsedNeighborhood(true);
    setUsedCuisine(true);
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
        "city": userCity.toLowerCase(),
        "res_mode_on": resMode,
        "res_date": resCriteria.date,
        "res_time": resCriteria.time,
        "party_size": resCriteria.partySize,
      };
    }
    // Otherwise, don't include those field (they're optional on the FastAPI side)
    else {
      idealMealData = {
        "description": input,
        "city": userCity.toLowerCase(),
        "res_mode_on": resMode,
      };
    }
    if (activeUser) {
      idealMealData['username'] = activeUser.username;
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
    if (responseJson.success) {
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
        setActiveKey(1);
      }
      setMessages((prev) => [
        ...prev.slice(0, prev.length - 1),
        {role: 'assistant', content: responseJson.pitch},
      ]);
      setUsedReservations(responseJson.usedReservations);
      setUsedBoth(responseJson.usedBoth);
      setUsedNeighborhood(responseJson.usedNeighborhood);
      setUsedCuisine(responseJson.usedCuisine);
      console.log("Used Reservation Mode: ", usedReservations);
      console.log("Used both filters: ", usedBoth);
      console.log("Used neighborhood filter:", usedNeighborhood);
      console.log("Used cuisine filter:", usedCuisine);
    }
    else {
      setMessages((prev) => [
        ...prev.slice(0, prev.length - 1),
        {role: 'assistant', content: responseJson.error},
      ]);
    }
    setChatIsLoading(false);
  }, [input, restoRecs]);

  return (
    <Page>
      <Head>
        <title>chompt</title>
        {/* Google tag (gtag.js) */}
        <script async src={"https://www.googletagmanager.com/gtag/js?id=G-0DKDCC3XSH"}/>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());

              gtag('config', 'G-0DKDCC3XSH');
            `,
          }}
        />
      </Head>
      <PrimerModal 
        isOpen={primerModalIsOpen} 
        setIsOpen={setPrimerModalIsOpen} 
        setSignupModalIsOpen={setSignupModalIsOpen}
        setLoginModalIsOpen={setLoginModalIsOpen}
      />
      <AboutModal isOpen={aboutModalIsOpen} setIsOpen={setAboutModalIsOpen} />
      <LoginModal 
        isOpen={loginModalIsOpen} 
        signupModalIsOpen={signupModalIsOpen}
        setIsOpen={setLoginModalIsOpen}
        setSignupModalIsOpen={setSignupModalIsOpen}
        activeUser={activeUser}
        setActiveUser={setActiveUser}
      >
      </LoginModal>
      <SignupModal 
        isOpen={signupModalIsOpen} 
        setIsOpen={setSignupModalIsOpen}
        activeUser={activeUser}
        setActiveUser={setActiveUser}
      >
      </SignupModal>
      <CityModal
        isOpen={cityModalIsOpen}
        setIsOpen={setCityModalIsOpen}
        userCity={userCity}
        setUserCity={setUserCity}
      >
      </CityModal>
      <ResModal
        isOpen={resModalIsOpen}
        setIsOpen={setResModalIsOpen}
        resMode={resMode}
        setResMode={setResMode}
        resCriteria={resCriteria}
        setResCriteria={setResCriteria}
        resModeToggleColor={resModeToggleColor}
        setResModeToggleColor={setResModeToggleColor}
      >
      </ResModal>
      <Header
        setRestoRecs={setRestoRecs}
        setAboutModalIsOpen={setAboutModalIsOpen}
        setLoginModalIsOpen={setLoginModalIsOpen}
        setSignupModalIsOpen={setSignupModalIsOpen}
        setCityModalIsOpen={setCityModalIsOpen}
        messages={messages}
        setMessages={setMessages}
        activeUser={activeUser}
        setActiveUser={setActiveUser}
        userCity={userCity}
        setUserCity={setUserCity}
      />
      <Tabs
        activeKey={activeKey}
        onChange={({ activeKey }) => {
          setActiveKey(activeKey);
        }}
        fill={FILL.fixed}
        activateOnFocus
        // overrides={{
        //   Root: {
        //     style: ({ $theme }) => ({
        //       height: "90%"
        //     })
        //   }
        // }}
      >
        <Tab title="Guru" 
        >
          <ChatView
            messages={messages}
            setMessages={setMessages}
            input={input}
            setInput={setInput}
            sendQuery={sendQuery}
            restoRecs={restoRecs}
            setRestoRecs={setRestoRecs}
            chatIsLoading={chatIsLoading}
            // setChatIsLoading={setChatIsLoading}
          />
        </Tab>
        <Tab title="Recs" 
        >
          <RestaurantsView
            restoRecs={restoRecs}
            resMode={resMode}
            resModalIsOpen={resModalIsOpen}
            setResMode={setResMode}
            setResModalIsOpen={setResModalIsOpen}
            usedReservations={usedReservations}
            usedBoth={usedBoth}
            usedNeighborhood={usedNeighborhood}
            usedCuisine={usedCuisine}
            userCity={userCity}
            resModeToggleColor={resModeToggleColor}
            setResModeToggleColor={setResModeToggleColor}
          />
        </Tab>
      </Tabs>
    </Page>
  );
};

export default Index;