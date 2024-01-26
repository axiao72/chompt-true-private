import {Modal, ModalHeader, ModalBody, ModalFooter, ModalButton} from 'baseui/modal';
import {Button, KIND, SIZE, SHAPE} from 'baseui/button';
import {useStyletron} from 'baseui';
import {ParagraphMedium, ParagraphSmall} from 'baseui/typography';
import {StyledLink} from 'baseui/link';
import { ArrowRight } from "baseui/icon";
import * as React from 'react';

export const PrimerModal = ({
  isOpen,
  setIsOpen,
  setLoginModalIsOpen,
  setSignupModalIsOpen,
  primerModalClosed,
  setPrimerModalClosed
}: {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  setLoginModalIsOpen: (isOpen: boolean) => void;
  setSignupModalIsOpen: (isOpen: boolean) => void;
  primerModalClosed: boolean;
  setPrimerModalClosed: (closed: boolean) => void;
}) => {
  const [, theme] = useStyletron();
  const handleClose = () => {
    setIsOpen(false);
  };
  const handleLogin = () => {
    setIsOpen(false);
    setLoginModalIsOpen(true);
  };
  const handleSignup = () => {
    setIsOpen(false);
    setSignupModalIsOpen(true);
  };
  const handleGuest = () => {
    setIsOpen(false);
    setPrimerModalClosed(true);
  };
  return (
    <Modal 
      // onClose={handleClose} 
      closeable={false} 
      isOpen={isOpen} 
      animate 
      autoFocus={false}
    >
      <ModalHeader>Welcome to Chompt!</ModalHeader>
      <ModalBody>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          It's truly a pleasure to have you.
        </ParagraphMedium>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          Once you're logged in, just type in as detailed (or vague) of a dining description as you'd like 
          and let us do the hard part - getting you up to 3 restaurant recommendations perfect for the occasion.
        </ParagraphMedium>
        {/* <ParagraphMedium color={theme.colors.contentSecondary}>
          Get creative! If you need some inspiration, think about something like 
          "Getting dinner on a Friday night with a group of friends and 
          we want Italian food. We're also going out after so we want a 
          place with good music and drinks." Please - have fun with it.
        </ParagraphMedium> */}
        <ParagraphMedium color={theme.colors.contentSecondary}>
          Feel free to {' '}
          {/* <StyledLink 
            href="#"
            onClick={handleLogin}
            style={{fontWeight: 'bold'}}
            // animateUnderline
            // target='_blank'
          >
            log in
          </StyledLink>
          {' '} or {' '}
          <StyledLink 
            href="#"
            onClick={handleSignup}
            style={{fontWeight: 'bold'}}
            // animateUnderline
            // target='_blank'
          >
            sign up
          </StyledLink> */}
          <StyledLink 
            href="#"
            onClick={handleGuest}
            style={{fontWeight: 700}}
            // animateUnderline
            // target='_blank'
          >
            continue as a guest
          </StyledLink>
          {''}, but joining the party is highly encouraged as we'll be getting more and more personalized.
        </ParagraphMedium>
      </ModalBody>
      <ModalFooter>
            {/* <Button
                size={SIZE.default}
                kind="tertiary"  
                onClick={handleGuest} 
                shape={SHAPE.default}
                endEnhancer={<ArrowRight/>}
                overrides={{
                    BaseButton: {
                        style: ({ $theme }) => ({
                            borderRadius:'8px',
                        })
                    }
                }}
            >
                Continue as guest
            </Button> */}
            <Button
                size={SIZE.default}
                kind="primary"  
                onClick={handleLogin} 
                shape={SHAPE.default}
                // endEnhancer={<ArrowRight/>}
                overrides={{
                    BaseButton: {
                        style: ({ $theme }) => ({
                            borderRadius:'8px',
                        })
                    }
                }}
            >
                Log in
            </Button>
            &nbsp;&nbsp; or &nbsp;&nbsp;
            <Button
                size={SIZE.default}
                kind="secondary"  
                onClick={handleSignup} 
                shape={SHAPE.default}
                // endEnhancer={<ArrowRight/>}
                overrides={{
                    BaseButton: {
                        style: ({ $theme }) => ({
                            borderRadius:'8px',
                        })
                    }
                }}
            >
                Sign up
            </Button>
        </ModalFooter>
    </Modal>
  );
};
