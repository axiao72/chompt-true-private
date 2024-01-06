import {Modal, ModalHeader, ModalBody, ModalFooter, ModalButton} from 'baseui/modal';
import {Button, KIND, SIZE, SHAPE} from 'baseui/button';
import {useStyletron} from 'baseui';
import {FormControl} from 'baseui/form-control';
import {Input} from 'baseui/input';
import {useState, useCallback} from 'react';
import type {User} from '../pages';

export const LoginModal = ({
    isOpen,
    signupModalIsOpen,
    setIsOpen,
    setSignupModalIsOpen,
    activeUser,
    setActiveUser,
  }: {
    isOpen: boolean;
    signupModalIsOpen: boolean
    setIsOpen: (isOpen: boolean) => void;
    setSignupModalIsOpen: (isOpen: boolean) => void;
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
    const handleSignup = () => {
        setIsOpen(false);
        setSignupModalIsOpen(true);
      };
    
    const handleLogin = useCallback(async () => {
        setIsLoading(true);
        console.log(username)
        console.log(password)
        // Log user in using username and password
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-type': 'application/json'
            },
            body: JSON.stringify({
                'username': username,
                'password': password
            }),
        });
        const responseJson = await response.json();
        if (responseJson.success) {
            const loggedInUser: User = {
                username: responseJson.username,
                firstName: responseJson.firstName,
                lastName: responseJson.lastName
            };
            console.log(loggedInUser.username);
            setActiveUser(loggedInUser);
            setIsOpen(false);
        }
        else {
            console.log(responseJson.error);
        }
        setIsLoading(false);
    }, [activeUser, username, password, setIsOpen]);

    return (
      <Modal onClose={handleClose} closeable isOpen={isOpen} animate autoFocus={false}>
        <ModalHeader>Log in</ModalHeader>
        <ModalBody>
            <FormControl >
                <Input
                    id="username-input-id"
                    value={username}
                    placeholder='Username'
                    onChange={(event) => setUsername(event.currentTarget.value)}
                    overrides={{
                        Root: {
                            style: ({ $theme }) => ({
                              borderRadius:'8px',
                            })
                        }
                    }}
                />
            </FormControl>
            <FormControl >
                <Input
                    id="password-input-id"
                    value={password}
                    placeholder='Password'
                    type='password'
                    onChange={(event) => setPassword(event.currentTarget.value)}
                    overrides={{
                        Root: {
                            style: ({ $theme }) => ({
                              borderRadius:'8px',
                            })
                        }
                    }}
                />
            </FormControl>
        </ModalBody>
        <ModalFooter>
            <ModalButton kind="tertiary" onClick={handleClose} shape={SHAPE.default}
                overrides={{
                    BaseButton: {
                        style: ({ $theme }) => ({
                            borderRadius:'8px',
                        })
                    }
                }}
            >
                Cancel
            </ModalButton>
            <ModalButton 
                onClick={handleLogin} 
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
                Let's Eat!
            </ModalButton>
        </ModalFooter>
      </Modal>
    );
  };