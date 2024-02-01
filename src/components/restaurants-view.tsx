import {styled, useStyletron} from 'baseui';
import {ParagraphSmall} from 'baseui/typography';
import {NAV_HEIGHT, type Document, RestoRec, User} from '../pages';
import {useState, useEffect, useRef, useCallback} from 'react';
import * as React from 'react';
import {
    Card,
    StyledBody,
    StyledAction
  } from "baseui/card";
import { StyledLink } from 'baseui/link';
import {Accordion, Panel} from 'baseui/accordion';
import { Button, SHAPE, SIZE, KIND as ButtonKIND } from "baseui/button";
import { StatefulTooltip } from "baseui/tooltip";
import { Checkbox, STYLE_TYPE, LABEL_PLACEMENT } from "baseui/checkbox";
import Image from "next/image";
import infoIcon from './icons/info_icon_1.png';
import {Block} from 'baseui/block';
import {Notification, KIND as NotiKIND} from 'baseui/notification';
import { ArrowRight, ChevronRight } from 'baseui/icon';
import ReactGA from 'react-ga4';


const Container = styled('div', ({$theme}) => ({
  // background: $theme.colors.backgroundPrimary,
  // overflow: 'auto',
  // display: 'flex',
  // flexDirection: 'column',
  // height: '65vh'
  
  // '@media only screen and (max-width: 650px)': {
  //   background: $theme.colors.backgroundPrimary,
  //   overflow: 'auto',
  //   display: 'flex',
  //   flexDirection: 'column',
  //   height: '65vh'
  // },

  '@media only screen and (max-width: 650px) and (max-height: 719px)': {
    background: $theme.colors.backgroundPrimary,
    overflow: 'auto',
    display: 'flex',
    flexDirection: 'column',
    height: '70vh'
  },

  '@media only screen and (max-width: 650px) and (min-height: 720px)': {
    background: $theme.colors.backgroundPrimary,
    overflow: 'auto',
    display: 'flex',
    flexDirection: 'column',
    height: '68vh'
  },

  '@media only screen and (min-width: 651px) and (max-width: 1024px)': {
    background: $theme.colors.backgroundPrimary,
    overflow: 'auto',
    display: 'flex',
    flexDirection: 'column',
    height: '70vh'
  },

  '@media only screen and (min-width: 1025px) and (max-width: 1400px)': {
    background: $theme.colors.backgroundPrimary,
    overflow: 'auto',
    display: 'flex',
    flexDirection: 'column',
    height: '75vh'
  },
  
  '@media only screen and (min-width: 1401px)': {
    background: $theme.colors.backgroundPrimary,
    overflow: 'auto',
    display: 'flex',
    flexDirection: 'column',
    height: '79vh'
  },
}));

const EmptyContainer = styled('div', {
  // flex: 1,
  display: 'flex',
  flexDirection: 'row',
  gap: '12px',
  overflowY: 'auto',
  padding: '16px',
  alignItems: 'center',
  justifyContent: 'center',
  height: '80vh'
});

const RecContainer = styled('div', ({$theme}) => ({
  // display: 'flex',
  background: $theme.colors.backgroundPrimary,
//   minHeight: '1000px',
  padding: '8px 16px',
  overflow: 'auto',
  overflowY: 'auto',
  overflowX: 'hidden',
//   display: 'webkit-box',
  flexDirection: 'column',
  gap: '50px',
//   justifyContent: 'center',
  alignItems: 'center',
  WebkitBoxOrient: 'vertical',
  WebkitBoxDirection: 'normal',
  WebkitBoxAlign: 'center',
  height: '80vh'
  
}));

const CardContainer = styled('div', {
  margin: '0 0 20px', // Adjust the margin as needed
});

const FeatureContainer = styled('div', ({$theme}) => ({
  padding: '0 0 6px 0',
  // borderBottom: `1px solid ${$theme.colors.borderOpaque}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}));

const FeatureGroup = styled('div', {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  gap: '2px',
  fontWeight: 550 
});

const ButtonContainer = styled('div', ({$theme}) => ({
  padding: '0 0 20px',
  // borderBottom: `1px solid ${$theme.colors.borderOpaque}`,
  display: 'flex',
  alignItems: 'center',
  // justifyContent: 'center',
  gap: '8px'
}));

const ButtonGroup = styled('div', {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: '2px',
  // width: '100%'
});

const FooterContainer = styled('div', ({$theme}) => ({
  display: 'flex',
  gap: '8px',
  borderTop: `1px solid ${$theme.colors.borderOpaque}`,
  // paddingTop: '16px',
  padding: '12px',
  justifyContent: 'center',
  alignItems: 'center',
  height: '5vh'
}));


const notNYC = (city: string) => {
  return city !== 'New York'
}

const Footer = ({resMode, clickResMode, setResModalIsOpen, userCity, resModeToggleColor}) => {
  const [, theme] = useStyletron();
  return (
    <FooterContainer>
      <Checkbox
        checked={resMode}
        checkmarkType={STYLE_TYPE.toggle_round}
        onChange={clickResMode}
        disabled={notNYC(userCity)}
        // disabled={false}
        labelPlacement={LABEL_PLACEMENT.right}
        overrides={{
          Toggle: {
            style: ({ $theme }) => ({
              backgroundColor: resModeToggleColor
            })
          }
        }}
      >
        Reservation Mode
      </Checkbox>
      <StatefulTooltip
        content={() => (
          <Block width={'250px'}>
            When Reservation Mode is enabled, only restaurants with available reservations for your desired date, 
            time, and party size will be recommended. <br></br><br></br>Reservation Mode only available in NYC (for now).
          </Block>
        )}
        returnFocus
        autoFocus
      >
        <Image
          src={infoIcon}
          width={15}
          height={15}
          alt="Information icon designed by Freepik"
          style={{ margin: '5px 0' }}
        />
      </StatefulTooltip>
      <Button
        onClick={() => setResModalIsOpen(true)}
        size={SIZE.mini}
        kind={ButtonKIND.tertiary}
      >
        Edit Filters
      </Button>
    </FooterContainer>
  );
};


const EmptyState = ({resMode, clickResMode, setResModalIsOpen, userCity, resModeToggleColor}) => {
  const [, theme] = useStyletron();
  return (
    <Container>
      <EmptyContainer>
        <ParagraphSmall color={theme.colors.contentTertiary}>
          To get a quick rundown, click the <b>chompt</b> logo in the top
          left!
        </ParagraphSmall>
      </EmptyContainer>
      <Footer 
        resMode={resMode} 
        clickResMode={clickResMode} 
        setResModalIsOpen={setResModalIsOpen} 
        userCity={userCity} 
        resModeToggleColor={resModeToggleColor}
      />
    </Container>
    
  );
};

const getMapsUrl = (restoName: string, address: string) => {
  const isAppleMobileDevice = /iPad|iPhone|iPod/.test(navigator.userAgent);
  console.log('Apple Device: ', isAppleMobileDevice);
  // If Apple device, return Apple Maps URL
  if (isAppleMobileDevice) {
    return getAppleMapsURL(restoName, address)
  }
  // If not, return Google Maps URL
  else {
    return getGoogleMapsURL(restoName, address)
  }
}

const getAppleMapsURL = (restoName: string, address: string) => {
  const encodedName = encodeURIComponent(restoName);
  const encodedAddress = encodeURIComponent(address);
  const appleMapsUrl = `https://maps.apple.com/?q=${encodedName}+${encodedAddress}`
  return appleMapsUrl
  // return 'https://maps.apple.com/?q=Hunan%20Slurp%20112%201st%20Ave,%20New%20York,%20NY%2010009'
}

const getGoogleMapsURL = (restoName: string, address: string) => {
  const encodedName = encodeURIComponent(restoName);
  const encodedAddress = encodeURIComponent(address);
  const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodedName}+${encodedAddress}`
  return googleMapsUrl
}

export const RestaurantsView = ({
  restoRecs,
  resMode,
  resModalIsOpen,
  setResMode,
  setResModalIsOpen,
  usedReservations,
  usedBoth,
  usedNeighborhood,
  usedCuisine,
  activeUser,
  userCity,
  resModeToggleColor,
  setResModeToggleColor
}: {
  restoRecs: Array<RestoRec>;
  resMode: boolean;
  resModalIsOpen: boolean;
  setResMode: (resModeOn: boolean) => void;
  setResModalIsOpen: (isOpen: boolean) => void;
  usedReservations: boolean;
  usedBoth: boolean;
  usedNeighborhood: boolean;
  usedCuisine: boolean;
  activeUser: User;
  userCity: string;
  resModeToggleColor: string;
  setResModeToggleColor: (color: string) => void;
}) => {
  const [, theme] = useStyletron();
  const containerRef = useRef();
  const [changedModes, setChangedModes] = useState(true);
  const [css] = useStyletron();
  const [isMobile, setIsMobile] = useState(true);
  const [loveButtonColors, setLoveButtonColors] = useState({0: '#EEEEEE', 1: '#EEEEEE', 2: '#EEEEEE'});
  const [hateButtonColors, setHateButtonColors] = useState({0: '#EEEEEE', 1: '#EEEEEE', 2: '#EEEEEE'});
  const [beenButtonColors, setBeenButtonColors] = useState({0: '#EEEEEE', 1: '#EEEEEE', 2: '#EEEEEE'});

  // Check if device is mobile
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 800); // Adjust the breakpoint as needed
    };

    // Initial check
    handleResize();

    // Add event listener for window resize
    window.addEventListener('resize', handleResize);

    // Cleanup the event listener on component unmount
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const handleLove = (index) => {
    console.log(index);
    const newColors = { ...loveButtonColors };
    if (newColors[index] === '#EEEEEE'){
      newColors[index] = '#06C167';
    }
    else {
      newColors[index] = '#EEEEEE';
    }
    setLoveButtonColors(newColors);
  };

  const handleHate = (index) => {
    console.log(index);
    const newColors = { ...hateButtonColors };
    if (newColors[index] === '#EEEEEE'){
      newColors[index] = '#E85C4A';
    }
    else {
      newColors[index] = '#EEEEEE';
    }
    setHateButtonColors(newColors);
  };

  const handleBeen = (index) => {
    console.log(index);
    const newColors = { ...beenButtonColors };
    if (newColors[index] === '#EEEEEE'){
      newColors[index] = '#A0BFF8';
    }
    else {
      newColors[index] = '#EEEEEE';
    }
    setBeenButtonColors(newColors);
  };

  const isLoved = (resto_name: string) => {

  };

  const isHated = (resto_name: string) => {

  };

  // const buttonColor = (resto_name: string) => {

  // };

  const clickResMode = () => {
    // Move this to an Apply button within the Modal so Res Mode only gets activated when user clicks "Apply". This should be when resMode get's changed
    
    // If Res Mode is off, then clicking the checkbox should just open the modal    
    // If Res Mode is on, clicking the checkbox should just turn Res Mode off 
    if (!resMode) {
      setResModalIsOpen(true);
    }
    else {
      setResMode(false);
      setResModeToggleColor('#FFFFFF');
    }
    // To keep track of res mode notification
    setChangedModes(true);
  };

  const clickBookRes = useCallback(async (resto: RestoRec) => {
    const currentDate = new Date();
    const dateString = currentDate.toISOString();
    if (resto.resyUrl) {
      window.open(resto.resyUrl, '_blank')
      ReactGA.event({
        category: 'button_click',
        action: 'clicked_book_reservation',
        label: resto.resyUrl
      });
      const eventData = {
        'event': 'button_click',
        'name': 'book_reservation',
        'value': resto.resyUrl,
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
    }
    else {
      window.open(resto.websiteUrl, '_blank')
      ReactGA.event({
        category: 'button_click',
        action: 'clicked_book_reservation',
        label: resto.websiteUrl
      });
      const eventData = {
        'event': 'button_click',
        'name': 'book_reservation',
        'value': resto.websiteUrl,
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
    }
  }, [restoRecs]);

  console.log(usedReservations);

  useEffect(() => {
    setChangedModes(false)

    if (restoRecs.length >= 1) {
      (containerRef.current as HTMLDivElement).scrollTo({
        //Add some padding to the scroll
        top: 0,
        behavior: 'smooth',
      });
    }
  }, [restoRecs]);

  if (restoRecs.length === 0) {
    // Render an Empty state which displays helpful message
    return <EmptyState 
            resMode={resMode} 
            clickResMode={clickResMode} 
            setResModalIsOpen={setResModalIsOpen} 
            userCity={userCity}
            resModeToggleColor={resModeToggleColor}
          />;
  }

  return (
    <Container>
      {resMode && !usedReservations && !changedModes &&
      <Notification 
        closeable
        kind={NotiKIND.warning}
        overrides={{
          Body: {style: {width: '85%', alignSelf: 'center'}},
        }}
      >
        Was not able to consider reservation availability for these recommendations 🥴 So, these spots may or may not have available reservations (blame Resy for not making their data easily accessible!)
      </Notification>}
      <RecContainer ref={containerRef}>
        {restoRecs.map((resto, index) => {
          return (
            <CardContainer key={`resto-${index}`}>
              <Card
                overrides={{Root: {style: {
                    width: '100%', 
                    flexDirection: 'column', 
                    alignItems: 'center',
                    WebkitBoxOrient: 'vertical', 
                    WebkitBoxDirection: 'normal',
                    WebkitBoxAlign: 'center',
                }}}}
                headerImage={resto.imageUrl}
                title={resto.restoName}
                // key={`resto-${index}`}
              >
                <StyledBody>
                  <FeatureContainer>
                    <FeatureGroup>
                      {resto.nbrhood}&nbsp;&nbsp;|&nbsp;&nbsp;{resto.priceRange}&nbsp;&nbsp;
                    </FeatureGroup>
                    <FeatureGroup>
                      <StyledLink 
                        as="a"
                        href={getMapsUrl(resto.restoName, resto.address)} 
                        target="_blank"
                        style={{ 
                          color: '#5B91F5', 
                          fontWeight: 700, 
                          display: 'flex',
                          alignItems: 'center' }}
                      >
                        Maps {<ChevronRight size={18} />}
                      </StyledLink>
                    </FeatureGroup>
                  </FeatureContainer>
                </StyledBody>
                {isMobile && 
                  <Accordion
                    overrides={{
                      Root: {
                        style: ({ $theme }) => ({
                          padding: '0px 0px 16px'
                        })
                      },
                      Content: {
                        style: ({ $theme }) => ({
                          fontSize: '14px',
                          padding: '8px 8px 16px'
                        })
                      },
                      Header: {
                        style: ({ $theme }) => ({
                          padding: '0px 0px 12px'
                        })
                      }
                    }}
                  >
                    <Panel
                      title={
                        <div
                          className={css({
                            display: 'flex', 
                            alignItems: 'center', 
                            fontWeight: 400, 
                            fontSize: '15px', 
                            padding: '0px 4px'
                          })}
                        >
                          {resto.review.split(" ").slice(0, 12).join(" ")}...
                        </div>
                      }
                    >
                      {resto.review}
                    </Panel>
                  </Accordion>
                }
                {!isMobile && 
                  <Accordion
                    overrides={{
                      Root: {
                        style: ({ $theme }) => ({
                          padding: '0px 0px 24px'
                        })
                      },
                      Content: {
                        style: ({ $theme }) => ({
                          fontSize: '15px',
                          padding: '8px 8px 24px'
                        })
                      },
                      Header: {
                        style: ({ $theme }) => ({
                          padding: '0px 0px 16px'
                        })
                      }
                    }}
                  >
                    <Panel
                      title={
                        <div
                          className={css({
                            display: 'flex', 
                            alignItems: 'center', 
                            fontWeight: 400, 
                            fontSize: '16px', 
                            padding: '0px 4px'
                          })}
                        >
                          {resto.review.split(" ").slice(0, 24).join(" ")}...
                        </div>
                      }
                    >
                      {resto.review}
                    </Panel>
                  </Accordion>
                }
                <ButtonContainer>
                  <Button
                    onClick={() => handleLove(index)}
                    kind={ButtonKIND.secondary}
                    shape={SHAPE.pill}
                    size={SIZE.mini}
                    disabled={hateButtonColors[index] != '#EEEEEE'}
                    overrides={{
                      BaseButton: {
                        style: ({ $theme }) => ({
                          backgroundColor: loveButtonColors[index],
                          width: '15%',
                          ':hover': {
                            backgroundColor: loveButtonColors[index]
                          }
                        })
                      }
                    }}
                  >
                    Love
                  </Button>
                  <Button
                    onClick={() => handleHate(index)}
                    kind={ButtonKIND.secondary}
                    shape={SHAPE.pill}
                    size={SIZE.mini}
                    disabled={loveButtonColors[index] !== '#EEEEEE'}
                    overrides={{
                      BaseButton: {
                        style: ({ $theme }) => ({
                          backgroundColor: hateButtonColors[index],
                          width: '15%',
                          ':hover': {
                            backgroundColor: hateButtonColors[index]
                          }
                        })
                      }
                    }}                  
                  >
                    Hate
                  </Button>
                  <Button
                    onClick={() => handleBeen(index)}
                    kind={ButtonKIND.secondary}
                    shape={SHAPE.pill}
                    size={SIZE.mini}
                    // disabled={loveButtonColors[index] !== '#EEEEEE'}
                    overrides={{
                      BaseButton: {
                        style: ({ $theme }) => ({
                          backgroundColor: beenButtonColors[index],
                          width: '25%',
                          ':hover': {
                            backgroundColor: beenButtonColors[index]
                          }
                        })
                      }
                    }}                  
                  >
                    I've Been
                  </Button>
                </ButtonContainer>
                <StyledAction>
                    <Button
                      overrides={{BaseButton: {style: {width: '100%', borderRadius:'8px'}}}} 
                      onClick={() => clickBookRes(resto)}
                      disabled={!resto.resyUrl && !resto.websiteUrl}
                    >
                        Book Reservation
                    </Button>
                </StyledAction>
              </Card>
            </CardContainer>
          );
        })}
      </RecContainer>
      <Footer 
        resMode={resMode} 
        clickResMode={clickResMode} 
        setResModalIsOpen={setResModalIsOpen} 
        userCity={userCity} 
        resModeToggleColor={resModeToggleColor}
      />
    </Container>
    
  );
};
