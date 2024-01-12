import {Modal, ModalHeader, ModalBody, ModalFooter, ModalButton} from 'baseui/modal';
import {useStyletron} from 'baseui';
import {FormControl} from 'baseui/form-control';
import {Input} from 'baseui/input';
import { DatePicker, StatefulDatePicker } from "baseui/datepicker";
import { TimePicker } from "baseui/timepicker";
import { Select, Value } from "baseui/select";
import {useState, useCallback} from 'react';
import {type ReservationCriteria} from '../pages';

export const ResModal = ({
    isOpen,
    setIsOpen,
    resMode,
    setResMode,
    resCriteria,
    setResCriteria
  }: {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
    resMode: boolean;
    resCriteria: ReservationCriteria;
    setResMode: (resModeOn: boolean) => void;
    setResCriteria: (resCriterida: ReservationCriteria) => void;
  }) => {
    const [, theme] = useStyletron();
    const [resDate, setResDate] = useState(new Date());
    const [resTime, setResTime] = useState(null);
    const [resPartySize, setResPartySize] = useState(null);
    const [partySizeNotSelected, setPartySizeNotSelected] = useState(false);
    const handleClose = () => {
      setIsOpen(false);
    };
    const handleApply = () => {
        // When user hits Apply, set resCriteria to the specified filters, set resMode to True, and close the modal
        if (resPartySize !== null) {
            const year = resDate.getFullYear();
            const month = (resDate.getMonth() + 1).toString().padStart(2, '0');
            const day = resDate.getDate().toString().padStart(2, '0');
            const formattedDate = `${year}-${month}-${day}`;
            const hours = resTime.getHours().toString().padStart(2, '0');
            const minutes = resTime.getMinutes().toString().padStart(2, '0');
            const timeString = `${hours}:${minutes}`;
            const criteria: ReservationCriteria = {
                date: formattedDate,
                time: timeString,
                partySize: resPartySize[0].id,
            }
            setResCriteria(criteria);
            setResMode(true);
            setIsOpen(false);
            console.log('Reservation Criteria: ', resCriteria)
        }
        else {
            setPartySizeNotSelected(true);
        }
    };
    
    return (
      <Modal onClose={handleClose} closeable isOpen={isOpen} animate autoFocus={false}>
        <ModalHeader>Tell me about your reservation</ModalHeader>
        <ModalBody>
            <FormControl label="Date">
                <DatePicker
                    value={resDate}
                    onChange={({date}) => setResDate(date as Date)}
                    // initialState={{value: []}}
                    formatString='yyyy-MM-dd'
                    placeholder="YYYY-MM-DD"
                    autoFocusCalendar={false}
                    overrides={{
                        Input: {
                          props: {
                            overrides: {
                              Root: {
                                style: ({ $theme }) => ({
                                    borderRadius:'8px',
                                  })
                              }
                            }
                          }
                        }
                    }}
                />
            </FormControl>
            <FormControl label="Time">
                <TimePicker
                    value={resTime}
                    // onChange={date => console.log(date)}
                    onChange={date => setResTime(date)}
                    // minTime={new Date()}
                    overrides={{
                        Select: {
                          props: {
                            overrides: {
                                ControlContainer: {
                                    style: ({ $theme }) => ({
                                        borderRadius:'8px',
                                    })
                                }
                            }
                          }
                        }
                    }}
                />
            </FormControl>
            <FormControl 
                label="Party size" 
                error={
                    partySizeNotSelected
                        ? 'Please choose a party size'
                        : null
                }
            >
                <Select
                    options={[
                        {
                            label: "2",
                            id: 2
                        },
                        {
                            label: "3",
                            id: 3
                        },
                        {
                            label: "4",
                            id: 4
                        },
                        {
                            label: "5",
                            id: 5
                        },
                        {
                            label: "6",
                            id: 6
                        },
                        {
                            label: "7",
                            id: 7
                        },
                        {
                            label:"8",
                            id: 8
                        }
                    ]}
                    value={resPartySize}
                    placeholder="Select party size"
                    error={partySizeNotSelected}
                    clearable={false}
                    // onChange={params => console.log(params.value)}
                    onChange={params => {setResPartySize(params.value); setPartySizeNotSelected(false);}}
                    overrides={{
                        ControlContainer: {
                            style: ({ $theme }) => ({
                                borderRadius:'8px',
                            })
                        }
                    }}
                />
            </FormControl>
        </ModalBody>
        <ModalFooter>
            <ModalButton kind="tertiary" onClick={handleClose}
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
            <ModalButton onClick={handleApply}
                overrides={{
                    BaseButton: {
                        style: ({ $theme }) => ({
                            borderRadius:'8px',
                        })
                    }
                }}
            >
                Apply
            </ModalButton>
        </ModalFooter>
      </Modal>
    );
  };
  