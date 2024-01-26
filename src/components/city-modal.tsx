import {Modal, ModalHeader, ModalBody, ModalFooter, ModalButton} from 'baseui/modal';
import {Button, KIND, SIZE, SHAPE} from 'baseui/button';
import {useStyletron} from 'baseui';
import {FormControl} from 'baseui/form-control';
import {Input} from 'baseui/input';
import {useState, useCallback} from 'react';
import { RadioGroup, Radio, ALIGN } from "baseui/radio";

export const CityModal = ({
    isOpen,
    setIsOpen,
    userCity,
    setUserCity,
  }: {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
    userCity: string;
    setUserCity: (city: string) => void;
  }) => {
    const [, theme] = useStyletron();

    const handleClose = () => {
      setIsOpen(false);
    };
    const handleSubmit = () => {
        setIsOpen(false);
        // setSignupModalIsOpen(true);
    };

    return (
      <Modal onClose={handleClose} closeable isOpen={isOpen} animate autoFocus={false}>
        <ModalHeader>What city are you eating in?</ModalHeader>
        <ModalBody>
            <RadioGroup
                value={userCity}
                onChange={e => setUserCity(e.currentTarget.value)}
                name="city"
                align={ALIGN.vertical}
            >
                <Radio value="New York">New York</Radio>
                <Radio value="Los Angeles">Los Angeles</Radio>
                <Radio value="Philadelphia">Philadelphia</Radio>
                <Radio value="Chicago">Chicago</Radio>
                <Radio value="Denver">Denver</Radio>
                <Radio value="Washington DC">Boston</Radio>
                <Radio value="Boston">Boston</Radio>
                <Radio value="Pittsburgh">Pittsburgh</Radio>
            </RadioGroup>
        </ModalBody>
        <ModalFooter>
            {/* <ModalButton kind="tertiary" onClick={handleClose} shape={SHAPE.default}
                overrides={{
                    BaseButton: {
                        style: ({ $theme }) => ({
                            borderRadius:'8px',
                        })
                    }
                }}
            >
                Cancel
            </ModalButton> */}
            {/* <ModalButton 
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
                Go!
            </ModalButton> */}
        </ModalFooter>
      </Modal>
    );
  };