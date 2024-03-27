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
import {ProfileModal} from '../components/profile-modal';
import {
  Tabs,
  Tab,
  FILL,
  StyledTabList,
  StyledTabPanel,
} from 'baseui/tabs-motion';
import {Grid, Cell} from 'baseui/layout-grid';
import ReactGA from 'react-ga4';

ReactGA.initialize('G-0DKDCC3XSH');


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
  restoId: string;
  restoName: string;
  review: string;
  perfectFor: string;
  priceRange: string;
  imageUrl ? : string;
  websiteUrl : string;
  nbrhood : string;
  resyUrl ? : string;
  address: string;
  // Flag will be 0, 1, or 2. 
  // 0 = Hated
  // 1 = Not flagged
  // 2 = Loved
  flag: number;
  // beenTo will be either 0 or 1. 0 = not been to, 1 = been to
  beenTo: number;
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
  firstName ? : string;
  lastName ? : string;
};


const Index = () => {
  const [aboutModalIsOpen, setAboutModalIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [restoRecs, setRestoRecs] = useState<RestoRec[]>([]);
  const [beenButtonColors, setBeenButtonColors] = useState(['#EEEEEE', '#EEEEEE', '#EEEEEE']);
  // 0 denotes hate, 1 denotes neutral, 2 denotes love
  const [flagArray, setFlagArray] = useState([1, 1, 1]);
  const [resMode, setResMode] = useState<boolean>(false);
  const [resModalIsOpen, setResModalIsOpen] = useState(false);
  const [resModeToggleColor, setResModeToggleColor] = useState('#FFFFFF');
  const [loginModalIsOpen, setLoginModalIsOpen] = useState(false);
  const [signupModalIsOpen, setSignupModalIsOpen] = useState(false);
  const [primerModalIsOpen, setPrimerModalIsOpen] = useState(false);
  const [cityModalIsOpen, setCityModalIsOpen] = useState(false);
  const [profileModalIsOpen, setProfileModalIsOpen] = useState(false);
  // Set the defaults to today's date and a time!
  // const currentDate = new Date();
  const [resCriteria, setResCriteria] = useState<ReservationCriteria>(null);
  const [usedReservations, setUsedReservations] = useState(true);
  const [usedBoth, setUsedBoth] = useState(true);
  const [usedNeighborhood, setUsedNeighborhood] = useState(true);
  const [usedCuisine, setUsedCuisine] = useState(true);
  const [activeUser, setActiveUser] = useState<User>({username: 'chompt_guest'});
  const [activeKey, setActiveKey] = useState<React.Key>(0);
  const [chatIsLoading, setChatIsLoading] = useState(false);
  const [userCoordinates, setUserCoordinates] = useState(null);
  const [userCity, setUserCity] = useState('New York');
  // To keep track if the primer modal was clicked through. Once clicked through, never show again (unless page refresh)
  const [primerModalClosed, setPrimerModalClosed] = useState(false);
  const supportedCities = ['new york', 'los angeles', 'philadelphia', 'chicago', 'denver', 'boston', 'pittsburgh'];

  const getUserFromUUID = async (uuid) => {
    console.log("Getting user from cookies session uuid: ", uuid);
    // Log user in using username and password
    const response = await fetch(`/api/get_mongo_user_from_uuid/${uuid}`, {
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
        setPrimerModalIsOpen(false);
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
      const cookie_uuid = document.cookie.replace(/(?:(?:^|.*;\s*)session_uuid\s*\=\s*([^;]*).*$)|^.*$/, "$1");
      const cookie_username = document.cookie.replace(/(?:(?:^|.*;\s*)chompt_username\s*\=\s*([^;]*).*$)|^.*$/, "$1");
      // console.log('Cookie Username: ', cookie_username, ' !!!');
      if (cookie_username !== '' && cookie_uuid !== '') {
        setActiveUser({'username': cookie_username});
        getUserFromUUID(cookie_uuid);
        // setPrimerModalIsOpen(false);
      }
      else {
        console.log('No uuid in cookies, user staysssss chompt_guest');
        setPrimerModalIsOpen(true)
        // setActiveUser("chompt_guest"); Don't think i need this, setting activeUser default value as 'chompt_guest'
      }
    }
    else {
      // Open primer modal to give user rundown if not already an active user
      if (activeUser.username === 'chompt_guest') {
        setPrimerModalIsOpen(true)
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
          const opencageApiKey = process.env.NEXT_PUBLIC_OPENCAGE_API_KEY;
          // console.log(process.env.NEXT_PUBLIC_OPENCAGE_API_KEY);
          // const opencageApiKey = '615ffe469cda4821adb01bd362b5692e';
          const opencageApiUrl = `https://api.opencagedata.com/geocode/v1/json?q=${latitude}+${longitude}&key=${opencageApiKey}`;

          try {
            const opencageResponse = await fetch(opencageApiUrl);
            const cityData = await opencageResponse.json();

            if (cityData.results && cityData.results.length > 0) {
              const city = cityData.results[0].components.city;
              if (supportedCities.includes(city.toLowerCase())){
                setUserCity(city);
                console.log(`User's location set to ${city}.`)
              }
              else {
                console.log("User's location is not one of supported cities. Defaulting to NYC.")
              }
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
  }, []);

  useEffect(() => {
    const newFlagArray = restoRecs.map((resto) => {
      if (resto.flag === 0) {
        return 0;
      } else if (resto.flag === 2) {
        return 2;
      } else {
        return 1;
      }
    });
    setFlagArray(newFlagArray);
    const newBeenColors = restoRecs.map((resto) => {
      if (resto.beenTo === 0) {
        return '#EEEEEE';
      } else {
        return '#A0BFF8';
      }
    });
    setBeenButtonColors(newBeenColors);
  }, [restoRecs]);

  const getColor = (index) => {
    console.log(flagArray);
    if (flagArray[index] === 0) {
      return '#E85C4A'
    } else if (flagArray[index] === 1) {
      return '#EEEEEE'
    } else {
      return '#06C167'
    }
  };

  const getHoverColor = (button: string, index: number) => {
    if (button === 'hate' && flagArray[index] === 2) {
      // Disabled Hate button case - can replace this with the disabled gray color
      return '#EEEEEE'
    } else if (button === 'love' && flagArray[index] === 0) {
      // Disabled Love button case - can replace this with the disabled gray color
      return '#EEEEEE'
    }
    else {
      getColor(index)
    }
  };

  const handleLove = (index: number, restoId: string) => {
    console.log(index);
    let operation = '';
    // const newColors = { ...loveButtonColors };
    // if (newColors[index] === '#EEEEEE') {
    //   newColors[index] = '#06C167';
    // }
    // else {
    //   newColors[index] = '#EEEEEE';
    // }
    // setLoveButtonColors(newColors);
    const newFlagArray = { ...flagArray };
    if (newFlagArray[index] === 1) {
      newFlagArray[index] = 2;
      operation = 'push';
    } else if (newFlagArray[index] === 2) {
      newFlagArray[index] = 1;
      operation = 'pull';
    }
    setFlagArray(newFlagArray);
    // Call update user resto API 
    updateUserResto(operation, 'love', restoId, activeUser.username);
  };

  const handleHate = (index: number, restoId: string) => {
    console.log(index);
    let operation = '';
    // const newColors = { ...hateButtonColors };
    // if (newColors[index] === '#EEEEEE'){
    //   newColors[index] = '#E85C4A';
    // }
    // else {
    //   newColors[index] = '#EEEEEE';
    // }
    // setHateButtonColors(newColors);
    const newFlagArray = { ...flagArray };
    if (newFlagArray[index] === 1) {
      newFlagArray[index] = 0;
      operation = 'push';
    } else if (newFlagArray[index] === 0) {
      newFlagArray[index] = 1;
      operation = 'pull';
    }
    setFlagArray(newFlagArray);
    // Call update user resto API 
    updateUserResto(operation, 'hate', restoId, activeUser.username);
  };

  const handleBeen = (index: number, restoId: string) => {
    console.log(index);
    let operation = '';
    const newColors = { ...beenButtonColors };
    if (newColors[index] === '#EEEEEE'){
      newColors[index] = '#A0BFF8';
      operation = 'push'
    }
    else {
      newColors[index] = '#EEEEEE';
      operation = 'pull'
    }
    setBeenButtonColors(newColors);
    // Call update user resto API
    updateUserResto(operation, 'beenTo', restoId, activeUser.username);
  };

  const updateUserResto = useCallback(async (operation: string, button: string, restoId: string, username: string) => {
    const queryParams = new URLSearchParams({
      operation: operation,
      button: button,
      resto_id: restoId,
      username: username,
    });
    const updateResponse = await fetch(`/api/update_user_resto/?operation=${operation}&button=${button}&resto_id=${restoId}&username=${username}`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }
    });
    const updateResponseJson = await updateResponse.json();
    if (!updateResponseJson.success) {
      console.log(`Could not update user's ${button} restaurants.`);
    }
  }, [restoRecs]);

  // console.log(`User coordinates set to: ${userCoordinates}`);
  // console.log(`User city set to: ${userCity}`);

  const sendQuery = useCallback(async () => {
    const currentDate = new Date();
    const dateString = currentDate.toISOString();
    if (!restoRecs) {
      return;
    }
    ReactGA.event({
      category: 'button_click',
      action: 'sent_query',
      label: input
    });
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
    console.log('Reservation Criteria: ', resCriteria)
    const eventData = {
      'event': 'button_click',
      'name': 'sent_query',
      'value': input,
      'date': dateString,
      'username': activeUser.username,
      'user_city': userCity.toLowerCase()
    };
    console.log('Event Data: ', eventData);
    const mongoResp = await fetch('/api/track_event', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-type': 'application/json'
      },
      body: JSON.stringify(eventData)
    });
    const mongoRespJson = await mongoResp.json();
    console.log('Logged event in Mongo: ', mongoRespJson.success)
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
    idealMealData['username'] = activeUser.username;
    
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
          const resto_json = JSON.parse(resto);
          const restoRec: RestoRec = {
            restoId: resto_json.restoId,
            restoName: resto_json.restoName,
            review: resto_json.review,
            perfectFor: resto_json.perfectFor,
            priceRange: resto_json.priceRange,
            imageUrl: resto_json.imageUrl,
            websiteUrl: resto_json.website,
            nbrhood: resto_json.neighborhood,
            resyUrl: resto_json.resyUrl,
            address: resto_json.fullAddress,
            flag: 1,
            beenTo: 1
          };
          if (activeUser.username != 'chompt_guest') {
            restoRec.flag = resto_json.flag;
            restoRec.beenTo = resto_json.beenTo;
          }
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
      // setUsedBoth(responseJson.usedBoth);
      // setUsedNeighborhood(responseJson.usedNeighborhood);
      // setUsedCuisine(responseJson.usedCuisine);
      console.log("Used Reservation Mode: ", usedReservations);
      // console.log("Used both filters: ", usedBoth);
      // console.log("Used neighborhood filter:", usedNeighborhood);
      // console.log("Used cuisine filter:", usedCuisine);
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
        <script async src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}/>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());

              gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}');
            `,
          }}
        />
      </Head>
      <PrimerModal 
        isOpen={primerModalIsOpen} 
        setIsOpen={setPrimerModalIsOpen} 
        setSignupModalIsOpen={setSignupModalIsOpen}
        setLoginModalIsOpen={setLoginModalIsOpen}
        primerModalClosed={primerModalClosed}
        setPrimerModalClosed={setPrimerModalClosed}
      />
      <AboutModal isOpen={aboutModalIsOpen} setIsOpen={setAboutModalIsOpen} />
      <LoginModal 
        isOpen={loginModalIsOpen} 
        signupModalIsOpen={signupModalIsOpen}
        primerModalIsOpen={primerModalIsOpen}
        setIsOpen={setLoginModalIsOpen}
        setSignupModalIsOpen={setSignupModalIsOpen}
        setPrimerModalIsOpen={setPrimerModalIsOpen}
        activeUser={activeUser}
        setActiveUser={setActiveUser}
        primerModalClosed={primerModalClosed}
        setPrimerModalClosed={setPrimerModalClosed}
      >
      </LoginModal>
      <SignupModal 
        isOpen={signupModalIsOpen} 
        primerModalIsOpen={primerModalIsOpen}
        setIsOpen={setSignupModalIsOpen}
        setPrimerModalIsOpen={setPrimerModalIsOpen}
        activeUser={activeUser}
        setActiveUser={setActiveUser}
        primerModalClosed={primerModalClosed}
        setPrimerModalClosed={setPrimerModalClosed}
      >
      </SignupModal>
      <CityModal
        isOpen={cityModalIsOpen}
        setIsOpen={setCityModalIsOpen}
        userCity={userCity}
        setUserCity={setUserCity}
      >
      </CityModal>
      <ProfileModal
        isOpen={profileModalIsOpen}
        setIsOpen={setProfileModalIsOpen}
        setLoginModalIsOpen={setLoginModalIsOpen}
        activeUser={activeUser}
        setActiveUser={setActiveUser}
      >
      </ProfileModal>
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
        setProfileModalIsOpen={setProfileModalIsOpen}
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
        <Tab title="Mr. Unlimited" 
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
            activeUser={activeUser}
            userCity={userCity}
            resModeToggleColor={resModeToggleColor}
            setResModeToggleColor={setResModeToggleColor}
            handleLove={handleLove}
            handleHate={handleHate}
            handleBeen={handleBeen}
            getColor={getColor}
            getHoverColor={getHoverColor}
            flagArray={flagArray}
            beenButtonColors={beenButtonColors}
          />
        </Tab>
      </Tabs>
    </Page>
  );
};

export default Index;