class AvailabilityManager {
    constructor() {
        this.csrftoken = this.getCookie('csrftoken');
        this.entryPoint = null;
        this.activeDateButton = null;
    }
    getCookie(name) {
        const cookie = document.cookie.split('; ').find(row => row.startsWith(name + '='));
        return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
    }
    csrfSafeMethod(method) {
        return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
    }
    setupAjax() {
        $.ajaxSetup({
            beforeSend: (xhr, settings) => {
                if (!this.csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", this.csrftoken);
                }
            }
        });
    }
    setupEntryPoint(){
        if ($('#gridContainer').length === 0) {
            $('#appointment_form .form-row.field-scheduled').children().first().hide();
            $('<div>', {
                class: 'form-row',
                id: 'gridContainer'
            }).appendTo('#appointment_form .form-row.field-scheduled')

            // $('#timeslot_form > div > fieldset').append('<div class="form-row" id="gridContainer"></div>');
        }
        this.entryPoint = $('#gridContainer')
    }
    setupDOM() {
        // Create the table container
        const availabilityContainer = $('<div>', { class: 'container-fluid' }).appendTo(this.entryPoint);

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
    }
    buildMonthYearSelector () { // Depends on setupDOM
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
            select.on('change', async (e) => {
                await this.getCalendarData()
                .then(response => {
                        this.buildCalendarTable(response)
                    })
                    .catch(err => console.log(err))
            });
            return select;
        };

        // Get current month and year
        const date = this.getDate()
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
    buildSlotTable (slots) { // Depends on slots, setupDOM
        const createSlot = (item, index) => {
            // Functions
            const createTableRow = () => $('<tr>'); // Function to create a new table row
            const createSlotButton = (item) => { // Function to create a button for a slot
                return $('<button>', {
                    type: 'button',
                    class: 'btn btn-sm',
                    text: this.formatTimeToAMPM(item.start_time)
                });
            };
            const createTableCell = (button) => { // Function to create a table cell with the provided button
                return $('<td>', {
                    class: 'text-center align-middle'
                }).append(button);
            };
            const handleButtonClick = (button) => { // Function to handle button click event
                console.log(button.data());
                this.postSlotData(button.data('id'), $('#id_user_phone_agent').val())
                    .then(response => {
                        this.formatColors(button, {table: "slot", label: response.data.invitees_allowed})
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
            this.formatColors(button, {table: "slot", label: item.invitees_allowed}) // Update the button color based on the slot status
            createTableCell(button).appendTo(row); // Create a table cell with the button and append it to the row
        }
        const timeContainer = $('#Availability-Time')
        // const dateStr = currentButton.data('date');
        const dateStr = "TEST"
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
    buildCalendarTable (data) { // Depends on data, setupDOM
        console.log(data)
        const date = this.getDate()

        // Clear the contents of the HTML container
        $('#Availability-Date').empty();
        $('#Availability-Time').empty();
        const days_of_week = data.days_of_week
        const weeks = data.weeks

        // Create the table structure
        const table = $('<table>', {class: "table table-striped table-hover"}).appendTo( $('#Availability-Date') );
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
                    const dateStr = this.formatDate(dateObj.date)
                    button.text(dateStr)
                    button.data({ slots: !!dateObj.slots, date: dateStr.toString(), date_obj: dateObj})
                    button.addClass('btn-primary')
                    // button.on('click', handleDateButtonClick);
                    button.on('click', async (ev) => {
                        const element = $(ev)[0].target
                        await this.getSlotData(dateObj.id)
                            .then(response => {
                                if (!!this.activeDateButton) {
                                    this.formatColors(this.activeDateButton, {table: "calendar", label: "unselected"})
                                }
                                this.formatColors(element, {table: "calendar", label: "selected"})
                                this.activeDateButton = element
                                $('#Availability-Time').empty();
                                console.log("Response: ", response)
                                this.buildSlotTable(response.slots)
                            })
                            .catch(err => console.log(err))
                    });
                } else {
                    button.text(`---`)
                    button.data({ slots: null })
                    button.addClass('btn-outline-secondary')
                    // button.disabled = true // not working
                }
            })
        })
    };
    async buildUI() { // Depends on setupDOM, buildMonthYearSelector, buildSlotTable, buildCalendarTable
        this.buildMonthYearSelector()
        await this.getCalendarData()
        .then(response => {
                this.buildCalendarTable(response)
            })
            .catch(err => console.log(err))

    }
    getDate() { // No Dependencies
        const monthElement = $('#monthSelector');
        const yearElement = $('#yearSelector');
        if (monthElement.length != 0 && yearElement.length != 0) {
            const month = monthElement[0].value;
            const year = yearElement[0].value;
            return new Date(year, month - 1, 5);
        }
        return new Date();
    }
    formatDate(dateString) { // No Dependencies
        const date = new Date(dateString);
        const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
        const month = months[date.getUTCMonth()];
        const day = String(date.getUTCDate()).padStart(2, '0');
        return `${month} ${day}`;
    }
    formatTimeToAMPM(timeString) { // No Dependencies
        const [hours, minutes] = timeString.split(':');
        const period = hours >= 12 ? 'PM' : 'AM';
        const adjustedHours = hours % 12 || 12;
        return `${adjustedHours}:${minutes} ${period}`;
    }
    formatColors(elementProp, designation){
        const element = $(elementProp)
        if (designation.table === "calendar") {
            if (designation.label === "selected"){
                element.addClass('btn-warning')
                element.removeClass('btn-primary')
            }
            if (designation.label === "unselected"){
                element.addClass('btn-primary')
                element.removeClass('btn-warning')
            }
        }
        if (designation.table === "slot") {
            if (designation.label === 0){
                element.addClass('btn-warning')
                element.removeClass('btn-primary')
            } else {
                element.addClass("btn-primary")
                element.removeClass("btn-warning")
            }
        }
    }
    async getCalendarData() { // Depends on getDate
        const date = this.getDate()
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        };
        const selectedDate = date.toLocaleString('en-US', options).replace(',', '');
        const userId = $('#id_user_field_agent').val();
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
    async getSlotData(date_id) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/availability/get_field_availability/',
                method: 'GET',
                data: { date_id: date_id },
                success: resolve,
                error: reject
            });
        });

    }
    async postSlotData (slot_id, phone_agent) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/availability/appointment_select_slot/',
                method: 'POST',
                // headers: {
                //     'X-CSRFToken': this.csrftoken
                // },
                data: { slot_id: slot_id, phone_agent: phone_agent},
                success: resolve,
                error: reject
            });
        });
    }
    init(){
        $(document).ready(() => {
            this.setupAjax();
            this.setupEntryPoint()
            this.setupDOM()
            $('#id_user_field_agent').parent().on('change', this.buildUI.bind(this));
        });
    }
}

// Initialize the script
const availabilityManager = new AvailabilityManager();
availabilityManager.init();