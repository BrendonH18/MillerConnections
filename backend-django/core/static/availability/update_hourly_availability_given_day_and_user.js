window.onload = function() {
    jQuery(function($) {
        const getCookie = name => {
            const cookie = document.cookie.split('; ').find(row => row.startsWith(name + '='));
            return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
        };
        const csrftoken = getCookie('csrftoken');

        const csrfSafeMethod = method => /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);

        $.ajaxSetup({
            beforeSend: (xhr, settings) => {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        $(document).ready(() => {
            $('.input-group.dbdp').addClass('flex-column');

            if ($('#gridContainer').length === 0) {
                $('#timeslot_form > div > fieldset').append('<div class="form-row" id="gridContainer"></div>');
            }

            $('#id_date').datetimepicker();

            const handleDateChange = (ev) => {
                const retrieveAvailabilityData = (ev) => {
                    const selectedDate = $(ev.target)[0] && Object.values($(ev.target)[0]).find(obj => obj?.date)?.date;
                    const userId = $('#id_user').val();

                    return new Promise((resolve, reject) => {
                        $.ajax({
                            url: '/availability/retrieve_time_slots/',
                            method: 'GET',
                            data: { user_id: userId, date: selectedDate },
                            success: resolve,
                            error: reject
                        });
                    });
                };

                const formatDateString = dateStr => {
                    const date = new Date(dateStr);
                    const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                    const shortMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    return `${daysOfWeek[date.getDay()]} (${shortMonths[date.getMonth()]} ${date.getDate()})`;
                };

                const toggleTimeSlot = (userId, date, time) => {
                    return new Promise((resolve, reject) => {
                        $.ajax({
                            url: '/availability/toggle_time_slot_by_user/',
                            method: 'POST',
                            data: { date, time, userId },
                            success: resolve,
                            error: reject
                        });
                    });
                };

                const buildCalendarTable = (HTMLSelector, weekStart, hoursList, availableDateTimes) => {
                    $(HTMLSelector).empty();
                    const tableContainer = $('<div id="tableContainer"></div>').on('click', 'button.btn', function() {
                        const element = $(this);
                        const date = element.data('date');
                        const time = element.data('time');
                        const userId = $('#id_user').val();

                        toggleTimeSlot(userId, date, time)
                            .then(response => {
                                element.toggleClass('btn-outline-primary btn-success');
                            })
                            .catch(error => console.error('Toggle failed:', error));
                    }).appendTo(HTMLSelector);

                    const table = $('<table class="table table-bordered"></table>').appendTo(tableContainer);
                    const thead = $('<thead></thead>').appendTo(table);
                    const tbody = $('<tbody></tbody>').appendTo(table);

                    const headerRow = $('<tr></tr>').appendTo(thead);
                    for (let i = 0; i < 7; i++) {
                        const currentDate = new Date(weekStart);
                        currentDate.setDate(currentDate.getDate() + i + 1);
                        $('<th scope="col">' + formatDateString(currentDate.toISOString().split('T')[0]) + '</th>').appendTo(headerRow);
                    }

                    hoursList.forEach(hour => {
                        const tr = $('<tr></tr>').appendTo(tbody);
                        for (let col = 0; col < 7; col++) {
                            const currentDate = new Date(weekStart);
                            currentDate.setDate(currentDate.getDate() + col);
                            const formattedDate = currentDate.toISOString().split('T')[0];
                            const ampm = hour >= 12 ? 'PM' : 'AM';
                            const displayHour = hour > 12 ? hour - 12 : hour || 12;
                            const button = $('<button type="button" class="btn"></button>').text(`${displayHour} ${ampm}`)
                                .data({ date: formattedDate, time: hour })
                                .addClass('btn-outline-primary');
                            
                            availableDateTimes.forEach(slot => {
                                if (slot.date === formattedDate && slot.time === hour) {
                                    button.removeClass('btn-outline-primary').addClass(slot.source === 'system' ? 'btn-success' : 'btn-warning');
                                }
                            });

                            $('<td></td>').append(button).appendTo(tr);
                        }
                    });
                };

                retrieveAvailabilityData(ev)
                    .then(data => buildCalendarTable('#gridContainer', data.week_start, data.possible_hours, data.available_times))
                    .catch(err => console.error('Error fetching data:', err));
            };
            $('#id_date').parent().on('dp.change', handleDateChange);
        });
    });
}