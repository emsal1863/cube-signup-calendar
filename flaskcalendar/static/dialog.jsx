class Dialog extends React.Component {


    constructor(x, y) {
        super();
        this.x = x;
        this.y = y;

    }

    render() {
        const divStyle = {
            color: '#f00',
            clear: 'both'
        };

        return <h1 style={divStyle}>aww yeah</h1>;
    }
}
