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

            // Initialize datetime picker
            $('#id_date').datetimepicker();

            // Event handler for date change
            const handleDateChange = (ev) => {

                // Function to retrieve availability data
                const retrieveAvailabilityData = (ev) => {
                    let selectedDate = "";
                    if ($(ev.target)[0].id == 'id_user') {
                        selectedDate = $('#id_date').val();
                    }
                    if ($(ev.target)[0].id == 'id_date') {
                        selectedDate = $(ev.target)[0] && Object.values($(ev.target)[0]).find(obj => obj?.date)?.date;
                    }

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

                // Function to format date string
                const formatDateString = dateStr => {
                    const date = new Date(dateStr);
                    const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                    const shortMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    return `${daysOfWeek[date.getDay()]} (${shortMonths[date.getMonth()]} ${date.getDate()})`;
                };

                // Function to toggle time slot
                const toggleTimeSlot = (userId, date, time, territoryId, source = 'button') => {
                    return new Promise((resolve, reject) => {
                        $.ajax({
                            url: '/availability/toggle_time_slot_by_user/',
                            method: 'POST',
                            data: { date, time, userId, territoryId, source },
                            success: resolve,
                            error: reject
                        });
                    });
                };
                const applyColors = () => {
                    $('#gridContainer button').each(function() {
                        const element = $(this);
                        const source = element.data('source');
                        if (source === 'user') {
                            element.addClass('btn-success').removeClass('btn-outline-primary');
                            element.css('background', '');
                        } else if (source === 'pending') {
                            element.addClass('btn-outline-primary').removeClass('btn-success');
                            element.css('background', 'white');
                        } else if (source === 'recurring') {
                            // Add code here for 'recurring' if needed in the future
                        } else if (source === 'settings') {
                            // Add code here for 'settings' if needed in the future
                        }
                    });
                };
                const triggerButton = (element, source = "button") => {
                    const date = element.data('date');
                    const time = element.data('time');
                    const userId = $('#id_user').val();
                    const territoryId = element.data('territoryId');

                    // Validate data attributes
                    if (!date || !time || !userId || !territoryId) {
                        console.error('Missing required data attributes:', { date, time, userId, territoryId });
                        return;
                    }

                    // Toggle the time slot
                    toggleTimeSlot(userId, date, time, territoryId, source)
                        .then(response => {
                            element.data({ date: response.date, time: response.hour, source: response.source, territoryId: response.territory });
                            applyColors()
                        })
                        .catch(error => console.error('Toggle failed:', error));
                };


                // Function to get first matching slot
                const getFirstMatching = (availableDateTimes, date) => {
                    const match = availableDateTimes.find(slot => slot.date === date);
                    return match ? match : null;
                };


                // Function to build calendar table
                const buildCalendarTable = (HTMLSelector, data) => {
                    console.log(data)
                    // Clear the contents of the HTML container
                    $(HTMLSelector).empty();
                    const days_of_week = data.days_of_week
                    const weeks = data.weeks

                    // Create the table container
                    const availabilityContainer = $('<div class="container-fluid"></div>')
                    availabilityContainer.appendTo(HTMLSelector)

                    const availabilitySelectorRow = $('<div class="row"></div>')
                    availabilityContainer.append(availabilitySelectorRow)

                    const availabilityCalendar = $('<div class="col-md-9"></div>')
                    const availabilityTimes = $('<div class="col-md-3"></div>')
                    availabilitySelectorRow.append(availabilityCalendar)
                    availabilitySelectorRow.append(availabilityTimes)

                    const availbilityCalendarResponsive = $('<div class="table-responsive"></div>')
                    availabilityCalendar.append(availbilityCalendarResponsive)
                    const dateContainer = $('<div id="Availability-Date"></div>')
                    availbilityCalendarResponsive.append(dateContainer)

                    const availbilityTimesResponsive = $('<div class="table-responsive"></div>')
                    availabilityTimes.append(availbilityTimesResponsive)
                    const timeContainer = $('<div id="Availability-Time"></div>')
                    availbilityTimesResponsive.append(timeContainer)



                    // Create the table structure
                    const table = $('<table class="table table-striped table-hover"></table>').appendTo(dateContainer);
                    const thead = $('<thead></thead>').appendTo(table);
                    const tbody = $('<tbody></tbody>').appendTo(table);

                    // Create the first header row for dates
                    const headerRow1 = $('<tr></tr>').appendTo(thead);
                    days_of_week.forEach(day => {
                        $('<th class="text-center align-middle" scope="col">' + day + '</th>').appendTo(headerRow1);
                    });
                    // for (let i = 0; i < 7; i++) {
                    //     const currentDate = new Date(weekStart);
                    //     currentDate.setDate(currentDate.getDate() + i + 1);
                    //     $('<th class="text-center align-middle" scope="col">' + formatDateString(currentDate.toISOString().split('T')[0]) + '</th>').appendTo(headerRow1);
                    // }

                    // Array to store initial selected values of territory select elements
                    // const initialTerritories = [];
                    // const headerRow2 = $('<tr></tr>').appendTo(thead);

                    // Create the second header row for territory selectors
                    // for (let i = 0; i < 7; i++) {
                    //     const currentDate = new Date(weekStart);
                    //     currentDate.setDate(currentDate.getDate() + i + 1);
                    //     const formattedDate = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`;

                    //     // Create a table header cell with a select element
                    //     const th = $('<th style="height: 70px; vertical-align: middle;" scope="col"></th>').appendTo(headerRow2);
                    //     const select = $('<select style="height: 40px; vertical-align: middle;" class="form-select"></select>').appendTo(th);

                    //     // Enable or disable the select based on the number of available territories
                    //     if (availableTerritories.length > 1) {
                    //         select.removeAttr('disabled');
                    //     } else {
                    //         select.attr('disabled', 'disabled');
                    //     }

                    //     // Add an empty option for no default value
                    //     $('<option></option>').appendTo(select);

                    //     // Populate the select with available territories
                    //     availableTerritories.forEach(territory => {
                    //         const firstMatching = getFirstMatching(availableDateTimes, formattedDate);
                    //         const option = $('<option></option>')
                    //             .val(territory.id)
                    //             .text(territory.name)
                    //             .appendTo(select);
                    //         if (firstMatching && territory.id == firstMatching.territory) {
                    //             option.prop('selected', true);
                    //         } else if (availableTerritories.length === 1) {
                    //             option.prop('selected', true);
                    //         }
                    //     });

                    //     // Store the initial selected value
                    //     initialTerritories.push(select.val());

                    //     // Event listener for select change to update buttons and column colors
                    //     select.on('change', function() {
                    //         const selectedTerritoryId = $(this).val();
                    //         const colorMapping = ['#adb5bd', '', '#0dcaf0']; // Colors for different ranks
                    //         const rank = $(this).find('option').index($(this).find('option:selected'));

                    //         // Update all buttons in this column with the selected territory
                    //         $(`#gridContainer td:nth-child(${i + 1}) button`).each(function() {
                    //             $(this).data('territoryId', selectedTerritoryId);
                    //             triggerButton($(this), 'dropdown')
                    //         });

                    //         // Update the background color of the column based on the rank
                    //         $(`#gridContainer td:nth-child(${i + 1})`).each(function() {
                    //             $(this).css('background-color', colorMapping[rank] || '');
                    //         });

                    //         applyColors()
                    //     });
                    // }

                    function formatDate(dateString) {
                        const date = new Date(dateString);
                        const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
                        const month = months[date.getUTCMonth()];
                        const day = String(date.getUTCDate()).padStart(2, '0');
                        return `${month} ${day}`;
                    }

                    let previousButton
                    async function handleDateButtonClick(event) {
                        timeContainer.empty()
                        if (previousButton) {
                            previousButton.addClass('btn-primary')
                            previousButton.removeClass('btn-warning')
                        }
                        currentButton = $(event.target)
                        currentButton.addClass('btn-warning')
                        currentButton.removeClass('btn-primary')
                        previousButton = currentButton
                        // const slots = currentButton.data('slots');
                        const dateStr = currentButton.data('date');
                        const dateObj = currentButton.data('date_obj');

                        async function retrieveSlotData (date_id) {
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

                        async function updateSlotData (slot_id) {
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
                        let slots
                        await retrieveSlotData(dateObj.id)
                            .then(response =>{
                                console.log("Response: ", response)
                                slots = response.slots
                            })
                            .catch(err => console.log(err))
                        


                        
                        // Create the table structure
                        const table = $('<table class="table table-striped table-hover"></table>').appendTo(timeContainer);
                        const thead = $('<thead></thead>').appendTo(table);
                        const tbody = $('<tbody id="time-table-body"></tbody>').appendTo(table);

                        // Create the first header row for dates
                        const headerRow = $('<tr></tr><tr></tr>').appendTo(thead);
                        // const bodyRow = $('<tr></tr> <tr></tr>').appendTo(tbody);
                        // const _body = $('#time-table-body').find('tr');
                        
                        const formatTimeToAMPM = timeString => {
                            const [hours, minutes] = timeString.split(':');
                            const period = hours >= 12 ? 'PM' : 'AM';
                            const adjustedHours = hours % 12 || 12;
                            return `${adjustedHours}:${minutes} ${period}`;
                        };
                        
                        $('<th class="text-center align-middle" scope="col">' + dateStr + '</th>').appendTo(headerRow);




                        slots.forEach((item, index) => {
                            if (index % 2 === 0) {
                                $('<tr></tr>').appendTo(tbody);
                            }
                            const row = tbody.children().last();
                            const button = $(`<button type="button" class="btn btn-sm">${formatTimeToAMPM(item.start_time)}</button>`)
                                .data(item) // Assuming 'start_time' as 'date'
                                .on('click', function() {
                                    console.log($(this).data());
                                    updateSlotData($(this).data('id'))
                                        .then(response => {
                                            if (response.status === "available") {
                                                $(this).removeClass("btn-primary")
                                                $(this).addClass("btn-warning")
                                            } else {
                                                $(this).addClass("btn-primary")
                                                $(this).removeClass("btn-warning")
                                            }
                                        })
                                        .catch(err => console.log(err))
                                });
                            if (item.status == "available") {
                                button.removeClass("btn-primary")
                                button.addClass("btn-warning")
                            } else {
                                button.addClass("btn-primary")
                                button.removeClass("btn-warning")
                            }
                            $(`<td class="text-center align-middle"></td>`).append(button).appendTo(row);
                        });
                        
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

                    // // Create table rows for each hour
                    // hoursList.forEach(hour => {
                    //     const tr = $('<tr></tr>').appendTo(tbody);
                    //     for (let col = 0; col < 7; col++) {
                    //         const currentDate = new Date(weekStart);
                    //         currentDate.setDate(currentDate.getDate() + col);
                    //         const formattedDate = currentDate.toISOString().split('T')[0];
                    //         const ampm = hour >= 12 ? 'PM' : 'AM';
                    //         const displayHour = hour > 12 ? hour - 12 : hour || 12;

                    //         // Create a button for each time slot
                    //         const button = $('<button type="button" class="btn"></button>')
                    //             .text(`${displayHour} ${ampm}`)
                    //             .data({ date: formattedDate, time: hour, territoryId: initialTerritories[col]})
                    //             // .addClass('btn-outline-primary');

                    //         // Update button class based on available date times
                    //         // availableDateTimes.forEach(slot => {
                    //         //     if (slot.date === formattedDate && slot.time === hour) {
                    //         //         button.data({ source: slot.source });
                    //         //     }
                    //         // });

                    //         // Append the button to the table cell
                    //         $('<td></td>').append(button).appendTo(tr);
                    //     }
                    // });

                    // // Trigger change event for each select element to update the buttons and column colors initially
                    // $('thead select').each(function() {
                    //     $(this).trigger('change');
                    //     applyColors()
                    // });
                    // $('#tableContainer').on('click', 'button.btn', function() {
                    //     triggerButton($(this))
                    //     applyColors()
                    // });
                    // applyColors()

                };


                retrieveAvailabilityData(ev)
                    .then(data => {
                        buildCalendarTable('#gridContainer', data)
                    })
                    .catch(err => console.error('Error fetching data:', err));
            };

            // Attach event handlers for date and user changes
            $('#id_date').parent().on('dp.change', handleDateChange);
            $('#id_user').parent().on('change', handleDateChange);
        });
    });
}
