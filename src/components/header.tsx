import {
  LabelSmall, LabelMedium, LabelLarge, DisplayXSmall, DisplaySmall, DisplayMedium, DisplayLarge,
  HeadingLarge,
  HeadingMedium,
  HeadingSmall,
  HeadingXSmall,
} from 'baseui/typography';
import Upload from 'baseui/icon/upload';
import {Button, KIND, SIZE, SHAPE} from 'baseui/button';
import { Avatar } from "baseui/avatar";
import {styled} from 'baseui';
import type {User, RestoRec, Message} from '../pages';
import { useCallback } from 'react';
import locationIcon from './icons/location.png';
import locationIcon2 from './icons/placeholder.png';
import Image from "next/image";

const Container = styled('div', ({$theme}) => ({
  // padding: '6px 16px',
  // // borderBottom: `1px solid ${$theme.colors.borderOpaque}`,
  // display: 'flex',
  // alignItems: 'center',
  // justifyContent: 'space-between',

  '@media only screen and (max-width: 650px)': {
    padding: '6px 16px',
    // borderBottom: `1px solid ${$theme.colors.borderOpaque}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },

  '@media only screen and (min-width: 651px)': {
    padding: '6px 28px',
    // borderBottom: `1px solid ${$theme.colors.borderOpaque}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },

}));

const Group = styled('div', {
  // display: 'flex',
  // alignItems: 'center',
  // justifyContent: 'space-between',
  // gap: '2px',
  '@media only screen and (max-width: 650px)': {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '2px',
  },

  '@media only screen and (min-width: 651px)': {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '12px',
  },
});

const TitleGroup = styled('div', {
  '@media only screen and (max-width: 650px)': {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '2px',
  },

  '@media only screen and (min-width: 651px)': {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '12px',
  },
  
});

export const Header = ({
  setRestoRecs,
  setAboutModalIsOpen,
  setLoginModalIsOpen,
  setSignupModalIsOpen,
  setCityModalIsOpen,
  messages,
  setMessages,
  activeUser,
  setActiveUser,
  userCity,
  setUserCity
}: {
  setRestoRecs: (recs: RestoRec[]) => void;
  setAboutModalIsOpen: (isOpen: boolean) => void;
  setLoginModalIsOpen: (isOpen: boolean) => void;
  setSignupModalIsOpen: (isOpen: boolean) => void;
  setCityModalIsOpen: (isOpen: boolean) => void;
  messages: Message[];
  setMessages: (messageArray: Message[]) => void;
  activeUser: User;
  setActiveUser: (user: User) => void;
  userCity: string;
  setUserCity: (city: string) => void;
}) => {
  const handleReset = () => {
    // Reset resto recs to empty
    setRestoRecs([]);
    // Reset chat messages to empty
    setMessages([]);
  };

  const handleLogout = () => {
    // Log user out (Finish implementing!)
    setActiveUser(null);
  };

  const handleAvatarClick = () => {
    console.log('clicked avatar!')
  }

  return (
    <Container>
      <TitleGroup>
        {/* <HeadingSmall margin='scale100'>
          chompt
        </HeadingSmall> */}
        <Button
          size={SIZE.mini}
          kind={KIND.tertiary}
          onClick={() => setAboutModalIsOpen(true)}
          shape={SHAPE.pill}
        >
          <HeadingSmall margin='scale100'>
            chompt
          </HeadingSmall>
          {/* About */}
        </Button>
        <Button 
          size={SIZE.mini}
          kind={KIND.tertiary}
          onClick={() => setCityModalIsOpen(true)}
          shape={SHAPE.pill}
          overrides={{
            BaseButton: {
              style: ({ $theme }) => ({
                // color: $theme.colors.contentTertiary, // Set the desired text color
                color: $theme.colors.accent300,
              }),
            },
          }}
        >
          <Image
            src={locationIcon2}
            width={15}
            height={15}
            alt="Location icon designed by Freepik"
            style={{ margin: '5px 0' }}
            // color='#6B6B6B'
            color='#5B91F5'
          />
          {userCity !== null ? <span>&nbsp;{userCity}</span> : <span>&nbsp;Choose City</span>}
        </Button>
      </TitleGroup>
      <Group>
        {/* <Button
          // startEnhancer={<Upload />}
          size={SIZE.mini}
          kind={KIND.tertiary}
          onClick={handleReset}
          shape={SHAPE.pill}
        >
          Reset
        </Button> */}
        {!activeUser && <Button
          // startEnhancer={<Upload />}
          size={SIZE.compact}
          kind={KIND.tertiary}
          onClick={() => setLoginModalIsOpen(true)}
          shape={SHAPE.pill}
        >
          Log in
        </Button>}
        {!activeUser && <Button
          // startEnhancer={<Upload />}
          size={SIZE.compact}
          kind={KIND.primary}
          onClick={() => setSignupModalIsOpen(true)}
          shape={SHAPE.pill}
        >
          Sign up
        </Button>}
        {activeUser && <Button onClick={handleAvatarClick} kind={KIND.tertiary} size={SIZE.default} shape={SHAPE.circle} overrides={{
            BaseButton: {
              style: ({ $theme }) => ({
                border: 'none',
                background: 'none',
                padding: 0
                // outline: `${$theme.colors.warning200} solid`,
                // backgroundColor: $theme.colors.warning200
              })
            }
          }}>
          <Avatar
            // startEnhancer={<Upload />}
            size="scale1000"
            name={activeUser.username}
            // src="https://avatars.dicebear.com/api/human/yard.svg?width=285&mood=happy"
          />
        </Button>
        }
        {activeUser && <Button
          // startEnhancer={<Upload />}
          size={SIZE.compact}
          kind={KIND.primary}
          onClick={handleLogout}
          shape={SHAPE.pill}
        >
          Logout
        </Button>}
      </Group>
    </Container>
  );
};
