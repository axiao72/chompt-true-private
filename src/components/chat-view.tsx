import {styled, useStyletron} from 'baseui';
import {ParagraphSmall} from 'baseui/typography';
import {Input} from 'baseui/input';
import {Button, KIND, SIZE, SHAPE} from 'baseui/button';
import {Skeleton} from 'baseui/skeleton';
import {ReactNode, useEffect, useRef, useState} from 'react';
import React from 'react';
import {Document, Message, RestoRec} from '../pages';
import {StyledLink} from 'baseui/link';

const Container = styled('div', ({$theme}) => ({

  '@media only screen and (max-width: 650px)': {
    background: $theme.colors.backgroundPrimary,
    overflow: 'auto',
    display: 'flex',
    flexDirection: 'column',
    height: '65vh'
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
  flexDirection: 'column',
  gap: '12px',
  overflowY: 'auto',
  padding: '16px',
  height: '80vh',
  alignItems: 'center',
  justifyContent: 'center'
});

const MessagesContainer = styled('div', {
  // flexGrow: 5,
  // flexBasis: '90%',
  // flexShrink: 0,
  // flex: 1,
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
  overflowY: 'auto',
  padding: '16px',
  height: '80vh'
});

const InputContainer = styled('div', ({$theme}) => ({
  // flexGrow: 1,
  // flexBasis: '10%',
  // flexShrink: 2,
  display: 'flex',
  gap: '16px',
  borderTop: `1px solid ${$theme.colors.borderOpaque}`,
  paddingTop: '16px',
  // padding: '16px',
  height: '10vh'
}));

const HeaderContainer = styled('div', ({$theme}) => ({
  display: 'flex',
  gap: '8px',
  // borderBottom: `1px solid ${$theme.colors.borderOpaque}`,
  // paddingTop: '16px',
  paddingTop: '12px',
  paddingBottom:'20px',
  justifyContent: 'center',
  alignItems: 'center',
  height: '10px'
}));

const InputBar = ({input, setInput, sendQuery}) => {
  const [, theme] = useStyletron();
  return (
    <InputContainer>
        <Input
          value={input}
          placeholder="Envision your perfect meal"
          onChange={(event) => setInput(event.currentTarget.value)}
          onKeyDown={(evt) => {
            if (evt.key === 'Enter') {
              sendQuery();
            }
          }}
          overrides={{
            Root: {
                style: ({ $theme }) => ({
                  borderRadius:'8px',
                })
            }
          }}
        />
        <Button type="submit" onClick={sendQuery}
          overrides={{
            BaseButton: {
                style: ({ $theme }) => ({
                    borderRadius:'8px',
                })
            }
        }}
        >
          Let's Ride
        </Button>
      </InputContainer>
  );
};

const EmptyState = ({input, setInput, sendQuery}) => {
  const [, theme] = useStyletron();
  return (
    <Container>
      <EmptyContainer>
        <ParagraphSmall color={theme.colors.contentTertiary}>
          Can't pick a spot? Tell me what's on your mind, I got you.
        </ParagraphSmall>
      </EmptyContainer>
      <InputBar input={input} setInput={setInput} sendQuery={sendQuery}/>
    </Container>
  );
};

const Message = ({
  children,
  role,
  isLoading,
}: {
  children: ReactNode;
  role: string;
  isLoading: boolean;
}) => {
  const [css, theme] = useStyletron();
  return (
    <div
      className={css({
        display: 'flex',
        flexDirection: 'column',
        gap: '0px',
        alignSelf: role === 'user' ? 'flex-end' : 'flex-start',
        alignItems: role === 'user' ? 'flex-end' : 'flex-start',
        background: theme.colors.backgroundSecondary,
        borderRadius: '8px',
        padding: '8px 12px',
      })}
    >
      <ParagraphSmall margin="0" color={theme.colors.contentTertiary}>
        {role === 'user' ? 'Me:' : 'Guru:'}
      </ParagraphSmall>
      {isLoading ? (
        <Skeleton width="300px" height="20px" animation />
      ) : (
        <ParagraphSmall margin="0">{children}</ParagraphSmall>
      )}
    </div>
  );
};
export const ChatView = ({
  messages,
  setMessages,
  input,
  setInput,
  sendQuery,
  restoRecs,
  setRestoRecs,
  chatIsLoading,
  // setChatIsLoading
}: {
  messages: Message[];
  setMessages: (messageArray: Message[]) => void;
  input: string;
  setInput: (text: string) => void;
  sendQuery: () => void;
  restoRecs: RestoRec[];
  setRestoRecs: (recs: RestoRec[]) => void;
  chatIsLoading: boolean;
  // setChatIsLoading: (isLoading: boolean) => void;
}) => {
  const [, theme] = useStyletron();
  const ref = useRef<HTMLDivElement | undefined>();

  useEffect(() => {
    //Ensure the most recent messages are visible
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
    }

  }, [messages]);
  
  // Render an Empty state component which displays a helpful message
  if (messages.length === 0) {
    return <EmptyState input={input} setInput={setInput} sendQuery={sendQuery}/>;
  }

  const handleReset = () => {
    // Reset resto recs to empty
    setRestoRecs([]);
    // Reset chat messages to empty
    setMessages([]);
  };

  return (
    <Container>
      <HeaderContainer>
        <Button
          size={SIZE.compact}
          kind={KIND.secondary}
          onClick={handleReset}
          shape={SHAPE.pill}
        >
          Reset
        </Button>
      </HeaderContainer>
      <MessagesContainer ref={ref}>
        {messages.map(({role, content, isLoading}, index) => {
          return (
            <Message
              key={`message-${role}-${index}`}
              role={role}
              isLoading={isLoading || false}
            >
              {content}
            </Message>
          );
      })}
      </MessagesContainer>
      <InputBar input={input} setInput={setInput} sendQuery={sendQuery}/>
    </Container>
  );
};
