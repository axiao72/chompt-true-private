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
}: {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  setLoginModalIsOpen: (isOpen: boolean) => void;
  setSignupModalIsOpen: (isOpen: boolean) => void;
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
  };
  return (
    <Modal onClose={handleClose} closeable isOpen={isOpen} animate autoFocus={false}>
      <ModalHeader>Welcome to Chompt! </ModalHeader>
      <ModalBody>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          Beyond excited to have you 🤩
        </ParagraphMedium>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          To get started, type in as detailed of a dining description as you'd like 
          and you'll receive 3 restaurant recommendations.
        </ParagraphMedium>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          If you need some inspiration, think about something like 
          "Getting dinner on a Friday night with a group of friends and 
          we want Italian food. We are also going out after so we want a 
          place with good music and drinks." Let your imagination free and have fun with it.
        </ParagraphMedium>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          Feel free to {' '}
          <StyledLink 
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
          </StyledLink>
          {' '} to join the party, we'll be getting more and more personalized as we go 🫡
        </ParagraphMedium>
      </ModalBody>
      <ModalFooter>
            <Button
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
            </Button>
        </ModalFooter>
    </Modal>
  );
};
