window.onload = function() {
    jQuery(function($) {

        // Function to get a specific cookie by name
        const getCookie = name => {
            const cookie = document.cookie.split('; ').find(row => row.startsWith(name + '='));
            return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
        };

        // Get CSRF token from cookies
        const csrftoken = getCookie('csrftoken');

        // Function to check if a method is CSRF safe
        const csrfSafeMethod = method => /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);

        // Set up AJAX with CSRF token for non-safe methods
        $.ajaxSetup({
            beforeSend: (xhr, settings) => {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        $(document).ready(() => {
            // Add 'flex-column' class to elements with 'input-group dbdp' class
            $('.input-group.dbdp').addClass('flex-column');

            // Append a div with id 'gridContainer' if it doesn't exist
            if ($('#gridContainer').length === 0) {
                $('#timeslot_form > div > fieldset').append('<div class="form-row" id="gridContainer"></div>');
            }
            

            
            const getDate = () => {
                const monthElement = document.getElementById('monthSelector');
                const yearElement = document.getElementById('yearSelector');
                let date = new Date();
                if (monthElement && yearElement) {
                    const month = monthElement.value;
                    const year = yearElement.value;
                    const day = 5;
                    date = new Date(year, month - 1, day);
                }
                return date
            }

            const buildMonthYearSelector = () => {
                // Constants for month names
                const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

                // Function to create and insert selectors
                const createSelector = (id, values, selectedValue) => {
                    const select = $('<select></select>').attr('id', id);
                    values.forEach(v => {
                        const option = new Option(v.text, v.value);
                        if (v.value === selectedValue) {
                            option.selected = true;
                        }
                        select.append(option);
                    });
                    select.on('change', handleDateChange);
                    return select;
                };

                // Get current month and year
                const date = getDate()
                const cMonth = date.getMonth() + 1; // JavaScript months are 0-based
                const cYear = date.getFullYear();

                // Create month and year selectors
                const monthSelector = createSelector(
                    'monthSelector',
                    monthNames.map((m, i) => ({ text: m, value: i + 1 })),
                    cMonth
                );
                const yearSelector = createSelector(
                    'yearSelector',
                    Array.from({ length: 3 }, (_, i) => ({ text: cYear - 1 + i, value: cYear - 1 + i })),
                    cYear
                );

                // Append selectors to the appropriate columns
                $('#monthSelectorCol').append(monthSelector);
                $('#yearSelectorCol').append(yearSelector);
 
            }

            // Event handler for date change
            const handleDateChange = (ev) => {

                // Function to retrieve availability data
                const retrieveAvailabilityData = (ev) => {
                    const date = getDate()
                    const options = { 
                        year: 'numeric', 
                        month: '2-digit', 
                        day: '2-digit', 
                        hour: '2-digit', 
                        minute: '2-digit', 
                        hour12: true 
                    };
                    selectedDate = date.toLocaleString('en-US', options).replace(',', '');
                    const userId = $('#id_user').val();
                    return new Promise((resolve, reject) => {
                        $.ajax({
                            url: '/availability/generate_calendar/',
                            method: 'GET',
                            data: { user_id: userId, date: selectedDate },
                            success: resolve,
                            error: reject
                        });
                    });
                };

                // Function to build calendar table
                const buildCalendarTable = (HTMLSelector, data) => {
                    console.log(data)
                    const date = getDate()
                    // Clear the contents of the HTML container
                    $(HTMLSelector).empty();
                    const days_of_week = data.days_of_week
                    const weeks = data.weeks

                    // Create the table container
                    const availabilityContainer = $('<div>', { class: 'container-fluid' }).appendTo(HTMLSelector);

                    // Create the row for selectors
                    const selectorRow = $('<div>', { class: 'row' }).appendTo(availabilityContainer);

                    // Define monthSelectorCol and yearSelectorCol so they can be used elsewhere
                    const monthSelectorCol = $('<div>', { class: 'col-md-6' , id: "monthSelectorCol" }).appendTo(selectorRow);
                    const yearSelectorCol = $('<div>', { class: 'col-md-6' , id: "yearSelectorCol"}).appendTo(selectorRow);

                    // Create the row for availability calendar and times
                    const availabilitySelectorRow = $('<div>', { class: 'row' }).appendTo(availabilityContainer);
                    const availabilityCalendar = $('<div>', { class: 'col-md-9' }).appendTo(availabilitySelectorRow);
                    const availabilityTimes = $('<div>', { class: 'col-md-3' }).appendTo(availabilitySelectorRow);

                    // Create responsive container for the calendar
                    const availabilityCalendarResponsive = $('<div>', { class: 'table-responsive' }).appendTo(availabilityCalendar);
                    const dateContainer = $('<div>', { id: 'Availability-Date' }).appendTo(availabilityCalendarResponsive);

                    // Create responsive container for the times
                    const availabilityTimesResponsive = $('<div>', { class: 'table-responsive' }).appendTo(availabilityTimes);
                    const timeContainer = $('<div>', { id: 'Availability-Time' }).appendTo(availabilityTimesResponsive);
                    
                    let previousButton

                    buildMonthYearSelector()

                    const buildDateSelector = () => {
                        
                    }
                    const formatDate = (dateString) => {
                        const date = new Date(dateString);
                        const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
                        const month = months[date.getUTCMonth()];
                        const day = String(date.getUTCDate()).padStart(2, '0');
                        return `${month} ${day}`;
                    }
                    // Create the table structure
                    const table = $('<table>', {class: "table table-striped table-hover"}).appendTo(dateContainer);
                    const thead = $('<thead>' , {}).appendTo(table);
                    const tbody = $('<tbody>', {}).appendTo(table);

                    // Create the first header row for dates
                    const headerRow1 = $('<tr>', {}).appendTo(thead);

                    days_of_week.forEach(day => {
                        $('<th>', { 
                            class: 'text-center align-middle', 
                            scope: 'col', 
                            text: day 
                        }).appendTo(headerRow1);
                    });
                    async function handleDateButtonClick(event) {
                        const handleDateColorUpdate = () => {
                            if (previousButton) {
                                previousButton.addClass('btn-primary')
                                previousButton.removeClass('btn-warning')
                            }
                            currentButton.addClass('btn-warning')
                            currentButton.removeClass('btn-primary')
                            previousButton = currentButton
                        }
                        const retrieveSlotData = async (date_id) => {
                            return new Promise((resolve, reject) => {
                                $.ajax({
                                    url: '/availability/generate_slots/',
                                    method: 'GET',
                                    data: { date_id: date_id },
                                    success: resolve,
                                    error: reject
                                });
                            });

                        }
                        const updateSlotData = async (slot_id) => {
                            return new Promise((resolve, reject) => {
                                $.ajax({
                                    url: '/availability/update_slot/',
                                    method: 'POST',
                                    data: { slot_id: slot_id },
                                    success: resolve,
                                    error: reject
                                });
                            });
                        }
                        const formatTimeToAMPM = timeString => {
                            const [hours, minutes] = timeString.split(':');
                            const period = hours >= 12 ? 'PM' : 'AM';
                            const adjustedHours = hours % 12 || 12;
                            return `${adjustedHours}:${minutes} ${period}`;
                        };

                        const buildSlotTable = (slots) => {
                            const handleSlotColorUpdate = (element, label) => {
                                if (label === "available") {
                                    element.removeClass("btn-primary")
                                    element.addClass("btn-warning")
                                    return
                                }
                                element.addClass("btn-primary")
                                element.removeClass("btn-warning")
                            }
                            const createSlot = (item, index) => {
                                // Functions
                                const createTableRow = () => $('<tr>'); // Function to create a new table row
                                const createSlotButton = (item) => { // Function to create a button for a slot
                                    return $('<button>', {
                                        type: 'button',
                                        class: 'btn btn-sm',
                                        text: formatTimeToAMPM(item.start_time)
                                    });
                                };
                                const createTableCell = (button) => { // Function to create a table cell with the provided button
                                    return $('<td>', {
                                        class: 'text-center align-middle'
                                    }).append(button);
                                };
                                const handleButtonClick = (button) => { // Function to handle button click event
                                    console.log(button.data());
                                    updateSlotData(button.data('id'))
                                        .then(response => {
                                            handleSlotColorUpdate(button, response.status);
                                        })
                                        .catch(err => console.log(err));
                                };
                                // Execution
                                const tableBody = $('#Availability-Time-Table-Body')
                                if (index % 2 === 0) { // Add a new row to the table body every two items
                                    createTableRow().appendTo(tableBody);
                                }
                                const row = tableBody.children().last(); // Get the last row added to tbody
                                const button = createSlotButton(item) // Create a button for the slot
                                    .data(item) // Attach the item data to the button
                                    .on('click', function() {
                                        handleButtonClick($(this)); // Handle button click event
                                    });
                                handleSlotColorUpdate(button, item.status); // Update the button color based on the slot status
                                createTableCell(button).appendTo(row); // Create a table cell with the button and append it to the row
                            }
                            const timeContainer = $('#Availability-Time')
                            const dateStr = currentButton.data('date');
                            // Create the table structure
                            const table = $('<table>', { class: 'table table-striped table-hover' }).appendTo(timeContainer);
                            const thead = $('<thead>', { }).appendTo(table);
                            const tbody = $('<tbody>', { id: 'Availability-Time-Table-Body' }).appendTo(table);
                            // Create the first header row for dates
                            const headerRow = $('<tr>', { }).appendTo(thead);
                            $('<th>', {  // Add Slot Header1
                                class: 'text-center align-middle', 
                                scope: 'col', 
                                text: dateStr 
                            }).appendTo(headerRow)
                            $('<th>', {  // Add Slot Header2
                                class: 'text-center align-middle', 
                                scope: 'col', 
                                text: "123" 
                            }).appendTo(headerRow)
                            slots.forEach((item, index) => { // Iterate over each slot item
                                createSlot(item, index)
                            });
                        }

                        const currentButton = $(event.target)
                        timeContainer.empty()
                        handleDateColorUpdate()
                        
                        // const slots = currentButton.data('slots');
                        const dateObj = currentButton.data('date_obj');
                        await retrieveSlotData(dateObj.id)
                        .then(response => {
                            console.log("Response: ", response)
                            buildSlotTable(response.slots)
                        })
                        .catch(err => console.log(err))
                    }
                    
                    
                    // Iterate over weeks and days to fill the table
                    weeks.forEach(week => {
                        const weekRow = $('<tr></tr>');
                        weekRow.appendTo(tbody)
                        week.forEach(day => {
                            const dayCell = $('<td class="text-center align-middle"></td>');
                            const button = $('<button type="button" class="btn btn-sm"></button>')
                            dayCell.append(button).appendTo(weekRow)
                            if (day.date_obj !== null) {
                                const dateObj = day.date_obj;
                                const dateStr = formatDate(dateObj.date)
                                button.text(dateStr)
                                button.data({ slots: !!dateObj.slots, date: dateStr.toString(), date_obj: dateObj})
                                button.addClass('btn-primary')
                                button.on('click', handleDateButtonClick);
                            } else {
                                button.text(`---`)
                                button.data({ slots: null })
                                button.addClass('btn-outline-secondary')
                                // button.disabled = true // not working
                            }
                        })
                    })
                };


                retrieveAvailabilityData(ev)
                    .then(data => {
                        buildCalendarTable('#gridContainer', data)
                    })
                    .catch(err => console.error('Error fetching data:', err));
            };

            // Attach event handlers for date and user changes
            $('#id_user').parent().on('change', handleDateChange);
        });
    });
}
