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
import { Button } from "baseui/button";

const Container = styled('div', ({$theme}) => ({
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

const EmptyState = () => {
  const [, theme] = useStyletron();
  return (
    <Container
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <ParagraphSmall color={theme.colors.contentTertiary}>
        To get a quick rundown, click the &quot;About&quot; button in the top
        right!
      </ParagraphSmall>
    </Container>
  );
};

export const RestaurantsView = ({
  restoRecs,
}: {
  restoRecs: Array<RestoRec>;
}) => {
  const [, theme] = useStyletron();
  const containerRef = useRef();

  const openResPage = ({
    url,
  }: {
    url: string;
  }) => {
    window.open(url, '_blank');
  };

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
    return <EmptyState />;
  }

  return (
    <Container ref={containerRef}>
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
    </Container>
  );
};
