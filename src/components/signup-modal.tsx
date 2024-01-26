import {Modal, ModalHeader, ModalBody, ModalFooter, ModalButton} from 'baseui/modal';
import {Button, KIND, SIZE, SHAPE} from 'baseui/button';
import {useStyletron} from 'baseui';
import {FormControl} from 'baseui/form-control';
import {Input} from 'baseui/input';
import {useState, useCallback} from 'react';
import type {User} from '../pages';

export const SignupModal = ({
    isOpen,
    primerModalIsOpen,
    setIsOpen,
    setPrimerModalIsOpen,
    activeUser,
    setActiveUser,
    primerModalClosed,
    setPrimerModalClosed
  }: {
    isOpen: boolean;
    primerModalIsOpen: boolean
    setIsOpen: (isOpen: boolean) => void;
    setPrimerModalIsOpen: (isOpen: boolean) => void;
    activeUser: User;
    setActiveUser: (user: User) => void;
    primerModalClosed: boolean;
    setPrimerModalClosed: (closed: boolean) => void;
  }) => {
    const [, theme] = useStyletron();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleClose = () => {
      setIsOpen(false);
      if (!primerModalClosed) {
        setPrimerModalIsOpen(true);
      }
    };
    
    const handleSignup = useCallback(async () => {
        setIsLoading(true);
        console.log(username);
        console.log(password);
        console.log(firstName);
        console.log(lastName);

        const newUser = {
            'username': username,
            'password': password,
            'first_name': firstName,
            'last_name': lastName
        };
        // Log user in using username and password
        const response = await fetch('/api/signup', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-type': 'application/json'
            },
            body: JSON.stringify(newUser),
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
            if (!primerModalClosed) {
                setPrimerModalClosed(true);
            }
        }
        else {
            console.log(responseJson.error);
        }
        setIsLoading(false);
    }, [activeUser, username, password, firstName, lastName, setIsOpen]);

    return (
      <Modal onClose={handleClose} closeable isOpen={isOpen} animate autoFocus={false}>
        <ModalHeader>Join the party!</ModalHeader>
        <ModalBody>
            <FormControl label='Who are you?'>
                <Input
                    id="firstname-input-id"
                    value={firstName}
                    placeholder='Enter your first name'
                    onChange={(event) => setFirstName(event.currentTarget.value)}
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
                    id="lastname-input-id"
                    value={lastName}
                    placeholder='Enter your last name'
                    onChange={(event) => setLastName(event.currentTarget.value)}
                    overrides={{
                        Root: {
                            style: ({ $theme }) => ({
                              borderRadius:'8px',
                            })
                        }
                    }}
                />
            </FormControl>
            <FormControl label='Username'>
                <Input
                    id="username-input-id"
                    value={username}
                    placeholder='Create a username'
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
            <FormControl label='Password'>
                <Input
                    id="password-input-id"
                    value={password}
                    placeholder='Create a password'
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
            <ModalButton 
                kind="tertiary" 
                onClick={handleClose} 
                shape={SHAPE.default} 
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
                onClick={handleSignup} 
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
                Sign me up!
            </ModalButton>
        </ModalFooter>
      </Modal>
    );
  };