class Dialog extends React.Component {


    constructor(calEvent, calendar) {
        super();

        this.calEvent = calEvent;
        this.calendar = calendar;

        this.state = {
            personValue: ''
        };

        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleDelete = this.handleDelete.bind(this);

    }

    handleSubmit(event) {
        var calEventId = this.props.calEvent._id;
        var calEvent = this.calEvent;

        var clientEvents = this.props.calendar.fullCalendar('clientEvents');
        var calEventTrue = clientEvents.find( (calEvent) => calEvent._id === calEventId);

        calEventTrue.title = this.state.personValue;

        this.props.calendar.fullCalendar('updateEvent', calEventTrue);
        this.props.calendar.fullCalendar('renderEvent', calEventTrue);

        $.ajax({
            url: '/calendar_event',
            contentType: 'application/json',
            method: 'PUT',
            data: JSON.stringify({
                id: calEventTrue.id,
                person: calEventTrue.title,
                start_time: calEventTrue.start,
                end_time: calEventTrue.end
            })
        });

        event.preventDefault();
        return false;
    }

    handleChange(event) {
        this.setState({personValue: event.target.value});
    }

    handleDelete(event) {
        console.log("Delete pressed");
    }

    render() {
        const divStyle = {
            color: '#f00'
        };

        return (
            <div style={divStyle}> <h1>Edit event -- {this.props.calEvent._id}</h1>
                <form onSubmit = {this.handleSubmit}>
                    <input name="person" value={this.state.personValue} onChange={this.handleChange} /> <br />
                    <input type="submit" value="Submit" />
                </form>
                <button onClick={this.handleDelete}>Delete</button>
            </div>
        );
    }
}
