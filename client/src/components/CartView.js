import React from 'react';

import { SidePane } from 'react-side-pane';
import Cookies from 'universal-cookie';

import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import Form from 'react-bootstrap/Form';

import CloseButton from 'react-bootstrap/CloseButton';

import isResponseOk from '../Utils';

const cookies = new Cookies();

export class CartItem {
    constructor (props) {
        this.name = props.name;
        this.quantity = props.quantity;
        this.uuid = props.uuid;
    }
}

export class CartItemView extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            item: props.item,
        };
    }

    render() {
        return (
            <p>{this.state.item.quantity}x {this.state.item.name}</p>
        );
    }
}

class CartView extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            open: props.open,
            onClose: props.onClose,
            checkoutModalOpen: false,
        };
    }

    componentWillReceiveProps(props) {
        this.setState({open: props.open});
    }

    close = () => {
        this.setState({open: false});
        this.state.onClose();
    }

    placeOrder = () => {
        fetch("/orders/place/", {
            method: "POST",
            headers: {
                "Content-Type" : "application/json",
                "X-CSRFToken" : cookies.get("csrftoken"),
            },
            credentials: "same-origin",
            body: JSON.stringify({'time' : new Date(this.state.orderTime)}),
        })
        .then(isResponseOk)
        .then(() => {
            this.setState({checkoutModalOpen: false, open: false});
        })
        .catch((err) => {
            console.log(err);
        });
    }

    handleCheckoutModalClose = () => {
        this.setState({checkoutModalOpen: false});
    }

    getOrderTimeOptions = () => {
        const intervalMinutes = 15;
        const endHours = 17;
        const endMinutes = 0;
        const endTotalMinutes = endHours * 60 + endMinutes;
        var date = new Date();
        var hours = date.getHours();
        var minutes = date.getMinutes();
        var totalMinutes = (hours + 1) * 60 + minutes;
        var nextAvailableTime = totalMinutes + ((intervalMinutes - (totalMinutes % intervalMinutes)) % intervalMinutes);
        var options = [];
        for (var i = nextAvailableTime; i <= endTotalMinutes; i += intervalMinutes) {
            var minutes = i % 60;
            var hours = parseInt((i - minutes) / 60);
            options.push(new Date(date.getFullYear(), date.getMonth(), date.getDate(), hours, minutes));
        }
        return options;
    }

    getTimeString = (date) => {
        var hours = date.getHours();
        var minutes = date.getMinutes();
        var am = true;
        if (hours >= 12) {
            am = false;
            if (hours > 12) {
                hours -= 12;
            }
        }
        return hours.toString() + ":" + minutes.toString().padStart(2, "0") + " " + (am ? "AM" : "PM");
    }

    openCheckoutModal = () => {
        var options = this.getOrderTimeOptions();
        var selection = options.count == 0 ? "" : options[0];
        this.setState({checkoutModalOpen: true, orderTime: selection, orderTimeOptions: options});
    }

    onSelectTime = (event) => {
        this.setState({orderTime: event.target.value});
    }

    render() {
        return (
            <div>
                <SidePane width={25} open={this.state.open}>
                    <div>
                        <CloseButton style={{position: "absolute", right: 10, top: 10}} onClick={this.close}></CloseButton>
                        <div style={{paddingLeft: 20, paddingTop: 20, paddingRight: 20}}>
                            {this.props.items.map((item) => <CartItemView item={item}></CartItemView>)}
                            {this.props.items.length == 0 && <p><i>No items in cart</i></p>}
                            <div className="d-grid gap-2">
                                <Button disabled={this.props.items.length == 0} className="rounded-pill" variant="secondary" onClick={this.openCheckoutModal}>
                                    Checkout
                                </Button>
                            </div>
                        </div>
                    </div>
                </SidePane>
                <Modal size="lg" show={this.state.checkoutModalOpen} onHide={this.handleCheckoutModalClose}>
                    <Modal.Header closeButton>
                        <Modal.Title>Checkout</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        {this.state.orderTimeOptions?.length > 0 ?
                            <div>
                                <p>When do you want it?</p>
                                <Form.Select onChange={this.onSelectTime} aria-label="Pick a time">
                                    {this.state.orderTimeOptions?.map((time) => <option value={time}>{this.getTimeString(time)}</option>)}
                                </Form.Select>
                            </div>
                            :
                            <p>There are currently no available order times</p>
                        }
                        <hr></hr>
                        {this.props.items.map((item) => <CartItemView item={item}></CartItemView>)}
                    </Modal.Body>
                    <Modal.Footer>
                        <Container>
                            <Row>
                                <Col><Button variant="secondary" onClick={this.handleCheckoutModalClose}>Close</Button></Col>
                                <Col><Button disabled={this.state.orderTimeOptions?.length == 0} className="float-end" variant="primary" onClick={this.placeOrder}>Place Order</Button></Col>
                            </Row>
                        </Container>
                    </Modal.Footer>
                </Modal>
            </div>
        );
    }
}

export default CartView;