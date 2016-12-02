class Dialog extends React.Component {


    constructor(calEventId, calendar) {
        super();

        this.calEventId = calEventId;
        this.calendar = calendar;

        this.state = {
            personValue: ''
        };

        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleChange = this.handleChange.bind(this);

    }

    handleSubmit(event) {
        var calEventId = this.props.calEventId;

        var clientEvents = this.props.calendar.fullCalendar('clientEvents');
        var calEventTrue = clientEvents.find( (calEvent) => calEvent._id === calEventId);

        calEventTrue.title = this.state.personValue;

        this.props.calendar.fullCalendar('updateEvent', calEventTrue);
        this.props.calendar.fullCalendar('renderEvent', calEventTrue);
        event.preventDefault();
        return false;
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
            <div style={divStyle}> <h1>Edit event --
            {this.props.calEventId}</h1>
                <form onSubmit = {this.handleSubmit}>
                    <input name="person" value={this.state.personValue} onChange={this.handleChange} />
                    <input type="submit" value="submit" />
                </form>
            </div>
        );
    }

}
