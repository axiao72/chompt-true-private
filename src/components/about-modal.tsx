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
          or honestly whatever you want to type in, and returns 3 restaurants you
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
          Some notable disclaimers:
          <ul>
            <li>In the overall scheme of NYC restaurants, the pool of restaurants in my database is pretty small. Keep that in mind while using the app,
              and I'll be working on getting more and more restaurants!
            </li>
            <li>The "Book Reservation" button will go directly to the restaurant's Resy page IF available. I currently only have a small 
              subset of restaurants linked to a Resy page, so if there's no Resy link available the button will go to the restaurant's 
              home page. </li>
            <li>Some recommended restaurants might be outdated or permanently closed, my data source includes old reviews 
              and I'm not currently checking for restaurant status (not my top priority rn but will address eventually!). </li>
            <li>Like everything else in this app, the interaction framework and flow is in progress. Stay tuned, more to come 😁 </li>
          </ul>
        </ParagraphMedium>
        <ParagraphMedium color={theme.colors.contentSecondary}>
          Made by Arthur Xiao (with some lovely help from the unknown Dylan Babbs). Please don't hesitate to reach
          out at axiao72@gmail.com with any feedback! Would love to hear both good and bad.
        </ParagraphMedium>
      </ModalBody>
    </Modal>
  );
};
