import {Modal, ModalHeader, ModalBody, ModalFooter, ModalButton} from 'baseui/modal';
import {Button, KIND, SIZE, SHAPE} from 'baseui/button';
import {useStyletron} from 'baseui';
import {FormControl} from 'baseui/form-control';
import {Input} from 'baseui/input';
import {useState, useCallback} from 'react';
import type {User} from '../pages';

export const ProfileModal = ({
    isOpen,
    setIsOpen,
    setLoginModalIsOpen,
    activeUser,
    setActiveUser,
  }: {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
    setLoginModalIsOpen: (isOpen: boolean) => void;
    activeUser: User;
    setActiveUser: (user: User) => void;
  }) => {
    const [, theme] = useStyletron();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleClose = () => {
      setIsOpen(false);
    };
    const handleLogout = useCallback(async () => {
        setIsLoading(true);
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-type': 'application/json'
            },
        });
        const responseJson = await response.json();
        if (responseJson.success) {
            setActiveUser({'username': 'chompt_guest'});
            setIsOpen(false);
        }
        else {
            console.log('Error clearing session from cookie (log out): ', responseJson.error);
        }
        // const pastDate = new Date(0);
        // document.cookie = `session_uuid=; expires=${pastDate.toUTCString()};`;
        setIsLoading(false);
    }, [activeUser]);

    return (
      <Modal 
        onClose={handleClose} 
        closeable 
        isOpen={isOpen} 
        animate 
        autoFocus={false}
        overrides={{
            Dialog: {
              style: {
                // width: '80vw',
                // height: '80vh',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '0 0 16px'
              },
            },
          }}
      >
        <ModalHeader>Hey {activeUser.firstName}!</ModalHeader>
        <ModalBody>
            <ModalButton 
                onClick={handleLogout} 
                shape={SHAPE.default}
                isLoading={isLoading}
                overrides={{
                    BaseButton: {
                        style: ({ $theme }) => ({
                            borderRadius:'8px',
                        })
                    }
                }}
            >
                Log out
            </ModalButton>
        </ModalBody>
      </Modal>
    );
  };