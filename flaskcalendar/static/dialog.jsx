class Dialog extends React.Component {


    constructor(x, y, calEvent, calendar) {
        super();

        this.state = {person: ''}

        this.x = x;
        this.y = y;
        this.calEvent = calEvent;
        this.calendar = calendar;

        this.state = {
            personValue: ''
        };

        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleChange = this.handleChange.bind(this);

    }

    handleSubmit(event) {
        var calEventId = this.props.calEvent._id;

        var clientEvents = this.props.calendar.fullCalendar('clientEvents');
        var calEventTrue = clientEvents.find( (calEvent) => calEvent._id === calEventId);

        calEventTrue.title = this.state.personValue;

        this.props.calendar.fullCalendar('updateEvent', calEventTrue);
        this.props.calendar.fullCalendar('renderEvent', calEventTrue);
        event.preventDefault();
    }

    handleChange(event) {
        this.setState({personValue: event.target.value});
    }

    render() {
        const divStyle = {
            color: '#f00',
            clear: 'both'
        };

        return (
            <div style={divStyle}>
                <h1>aww yeah</h1>
                <form onSubmit = {this.handleSubmit}>
                    <input name="person" onChange={this.handleChange} />
                    <input type="submit" value="submit" />
                </form>
            </div>
        );
    }
}
