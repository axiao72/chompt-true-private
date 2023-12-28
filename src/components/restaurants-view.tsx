import {styled, useStyletron} from 'baseui';
import {ParagraphSmall} from 'baseui/typography';
import {NAV_HEIGHT, type Document, RestoRec} from '../pages';
import {useEffect, useRef} from 'react';
import * as React from 'react';
import {
    Card,
    StyledBody,
    StyledAction
  } from "baseui/card";
import { Button, SIZE, KIND as ButtonKIND } from "baseui/button";
import { StatefulTooltip } from "baseui/tooltip";
import { Checkbox } from "baseui/checkbox";
import Image from "next/image";
import infoIcon from './icons/info_icon_1.png';
import {Block} from 'baseui/block';
import {Notification, KIND as NotiKIND} from 'baseui/notification';

const Container = styled('div', ({$theme}) => ({
  background: $theme.colors.backgroundPrimary,
  overflow: 'auto',
  display: 'flex',
  flexDirection: 'column',
}));

const EmptyContainer = styled('div', {
  flex: 1,
  display: 'flex',
  flexDirection: 'row',
  gap: '12px',
  overflowY: 'auto',
  padding: '16px',
  alignItems: 'center',
  justifyContent: 'center'
});

const RecContainer = styled('div', ({$theme}) => ({
  background: $theme.colors.backgroundPrimary,
//   minHeight: '1000px',
  padding: '8px 16px',
  overflow: 'auto',
  overflowY: 'auto',
  overflowX: 'hidden',
//   display: 'webkit-box',
  flexDirection: 'column',
  rowGap: '10px',
//   justifyContent: 'center',
  alignItems: 'center',
  WebkitBoxOrient: 'vertical',
  WebkitBoxDirection: 'normal',
  WebkitBoxAlign: 'center',
  
}));

const FooterContainer = styled('div', ({$theme}) => ({
  display: 'flex',
  gap: '8px',
  borderTop: `1px solid ${$theme.colors.borderOpaque}`,
  // paddingTop: '16px',
  padding: '12px',
  justifyContent: 'center'
}));


const EmptyState = ({resMode, clickResMode, setResModalIsOpen}) => {
  const [, theme] = useStyletron();
  return (
    <Container>
      <EmptyContainer>
        <ParagraphSmall color={theme.colors.contentTertiary}>
          To get a quick rundown, click the &quot;About&quot; button in the top
          right!
        </ParagraphSmall>
      </EmptyContainer>
      <FooterContainer>
        <Checkbox
          checked={resMode}
          onChange={clickResMode}
        >
          Reservation Mode
        </Checkbox>
        <StatefulTooltip
          content={() => (
            <Block width={'500px'}>
              When Reservation Mode is enabled, only restaurants with available reservations for your desired date, 
              time, and party size will be recommended.
            </Block>
          )}
          returnFocus
          autoFocus
        >
          <Image
            src={infoIcon}
            width={15}
            height={15}
            alt="Information icon"
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
    </Container>
    
  );
};

export const RestaurantsView = ({
  restoRecs,
  resMode,
  resModalIsOpen,
  setResMode,
  setResModalIsOpen,
  usedReservations
}: {
  restoRecs: Array<RestoRec>;
  resMode: boolean;
  resModalIsOpen: boolean;
  setResMode: (resModeOn: boolean) => void;
  setResModalIsOpen: (isOpen: boolean) => void;
  usedReservations: boolean;
}) => {
  const [, theme] = useStyletron();
  const containerRef = useRef();

  const clickResMode = () => {
    // Move this to an Apply button within the Modal so Res Mode only gets activated when user clicks "Apply". This should be when resMode get's changed
    // If Res Mode is off, then clicking the checkbox should just open the modal    
    // If Res Mode is on, clicking the checkbox should just turn Res Mode off 
   
    if (!resMode) {
      setResModalIsOpen(true)
    }
    else {
      setResMode(false);
    }
  };

  // const openResPage = ({
  //   url,
  // }: {
  //   url: string;
  // }) => {
  //   window.open(url, '_blank');
  // };
  console.log(usedReservations);

  useEffect(() => {
    if (restoRecs.length >= 1) {
      (containerRef.current as HTMLDivElement).scrollTo({
        //Add some padding to the scroll
        top: 0,
        behavior: 'smooth',
      });
    }
  }, [restoRecs]);

  if (restoRecs.length === 0) {
    return <EmptyState resMode={resMode} clickResMode={clickResMode} setResModalIsOpen={setResModalIsOpen}/>;
  }

  return (
    <Container>
      {resMode && !usedReservations && 
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
            <Card
              overrides={{Root: {style: {
                  width: '100%', 
                  // display:'webkit-box', 
                  flexDirection: 'column', 
                  alignItems: 'center',
                  WebkitBoxOrient: 'vertical', 
                  WebkitBoxDirection: 'normal',
                  WebkitBoxAlign: 'center',
                  // overflow: 'auto',
              }}}}
              headerImage={resto.imageUrl}
              title={resto.restoName}
              key={`resto-${index}`}
            >
              <StyledBody>
                  {resto.review}
              </StyledBody>
              <StyledBody>
                  {resto.nbrhood}&nbsp;&nbsp;|&nbsp;&nbsp;{resto.priceRange}&nbsp;&nbsp; 
                  {/* <a href={resto.websiteUrl} target="_blank">
                    {resto.restoName} Website
                  </a> */}
              </StyledBody>
              <StyledAction>
                  <Button
                    overrides={{BaseButton: {style: {width: '100%'}}}} 
                    onClick={resto.resyUrl ? () => window.open(resto.resyUrl, '_blank') : () => window.open(resto.websiteUrl, '_blank')}
                    disabled={!resto.resyUrl && !resto.websiteUrl}
                  >
                      Book Reservation
                  </Button>
              </StyledAction>
            </Card>
          );
        })}
      </RecContainer>
      <FooterContainer>
        <Checkbox
          checked={resMode}
          onChange={clickResMode}
        >
          Reservation Mode
        </Checkbox>
        <StatefulTooltip
          content={() => (
            <Block width={'500px'}>
              When Reservation Mode is enabled, only restaurants with available reservations for your desired date, 
              time, and party size will be recommended.
            </Block>
          )}
          returnFocus
          autoFocus
        >
          <Image
            src={infoIcon}
            width={15}
            height={15}
            alt="Information icon"
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
    </Container>
    
  );
};
