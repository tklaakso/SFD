import React from 'react';

import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Button from 'react-bootstrap/Button';

class TopBar extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            onViewCart: props.onViewCart,
        }
    }

    render() {
        return (
            <Navbar bg="dark">
                <Container>
                    <Navbar.Toggle />
                    <Navbar.Collapse className="justify-content-end">
                        <Button variant="primary" onClick={this.state.onViewCart}>View Cart</Button>
                    </Navbar.Collapse>
                </Container>
            </Navbar>
        );
    }
}

export default TopBar;