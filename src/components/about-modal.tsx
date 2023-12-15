import {Modal, ModalHeader, ModalBody} from 'baseui/modal';
import {useStyletron} from 'baseui';
import {ParagraphMedium} from 'baseui/typography';
import {StyledLink} from 'baseui/link';

export const AboutModal = ({
  isOpen,
  setIsOpen,
}: {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}) => {
  const [, theme] = useStyletron();
  const handleClose = () => {
    setIsOpen(false);
  };
  return (
    <Modal onClose={handleClose} closeable isOpen={isOpen} animate autoFocus>
      <ModalHeader>CHOMPT - The only restaurant chooser you'll ever need</ModalHeader>
      <ModalBody>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          This application takes in a description of a restaurant, meal, night out, 
          or honestly whatever you want to type in, and returns 4 restaurants you
          should go to without a doubt (no more scrolling through Yelp, Google,
          Beli, or whatever app you use to decide where to eat for hours on hours). 
          All of the grunt work is taken care of for you, it just involves a little 
          <i> truss</i> 😉 Don't worry, you're in good hands; the recommendations are 
          derived from professional reviews of the best restaurants in NYC. 
          Like Mr. Unlimited says himself - Broncos Country, Let's Ride.
        </ParagraphMedium>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          To get started, type in as detailed of a meal description as you'd like 
          and you will receive your 3 recommendations on the left hand side of the 
          screen. 
        </ParagraphMedium>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          If you need some inspiration, think about something like 
          "Getting dinner on a Friday night with a group of friends and 
          we want Italian food. We are also going out after so we want a 
          place with good music and drinks." Have fun with it.
        </ParagraphMedium>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          Made by Arthur Xiao (with some lovely help from the unknown Dylan Babbs)
        </ParagraphMedium>
      </ModalBody>
    </Modal>
  );
};
