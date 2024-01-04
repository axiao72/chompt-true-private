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

const Container = styled('div', ({$theme}) => ({
  padding: '6px 10px',
  // borderBottom: `1px solid ${$theme.colors.borderOpaque}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}));

const Group = styled('div', {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  gap: '2px',
});

const TitleGroup = styled('div', {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  gap: '4px',
});

export const Header = ({
  setRestoRecs,
  setAboutModalIsOpen,
  setLoginModalIsOpen,
  setSignupModalIsOpen,
  messages,
  setMessages,
  activeUser,
  setActiveUser
}: {
  setRestoRecs: (recs: RestoRec[]) => void;
  setAboutModalIsOpen: (isOpen: boolean) => void;
  setLoginModalIsOpen: (isOpen: boolean) => void;
  setSignupModalIsOpen: (isOpen: boolean) => void;
  messages: Message[];
  setMessages: (messageArray: Message[]) => void;
  activeUser: User;
  setActiveUser: (user: User) => void;
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
        <HeadingSmall margin='scale100'>
          chompt
        </HeadingSmall>
        <Button
          size={SIZE.compact}
          kind={KIND.tertiary}
          onClick={() => setAboutModalIsOpen(true)}
          shape={SHAPE.pill}
        >
          About
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
