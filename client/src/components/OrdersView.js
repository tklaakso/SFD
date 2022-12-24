import React from 'react';

import Card from 'react-bootstrap/Card';

import { Address } from './RestaurantBrowser';

import { postJson, getJson } from "../Utils";

class Order {
    constructor (props) {
        this.uuid = props.uuid;
        this.time = props.time;
        this.restaurants = props.restaurants;
        this.price = props.price;
        this.address = new Address(props.address);
    }
}

class OrderView extends React.Component {
    constructor (props) {
        super(props);
    }

    onClick = () => {
        this.props.onClick(this.props.order);
    }

    render() {
        return (
            <a style={{ cursor: "pointer" }} onClick={this.onClick}>
                <Card className="card-item" style={{ marginBottom: "10px", marginTop: "10px" }}>
                    <Card.Body>
                        <Card.Title>
                            {this.props.order.restaurants.join(", ")}
                        </Card.Title>
                        <Card.Text>
                            Delivering to {this.props.order.address.toString()}
                        </Card.Text>
                        <Card.Text>
                            ${this.props.order.price}
                        </Card.Text>
                    </Card.Body>
                </Card>
            </a>
        );
    }
}

class OrdersView extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            orders: null,
        }
    }

    getOrders = () => {
        getJson("/orders/view_all/")
        .then((orders) => {
            this.setState({orders: orders.map((order) => new Order(order))});
        });
    }

    render() {
        if (this.state.orders == null) {
            this.getOrders();
            return <></>;
        }
        return (
            <div>
                {this.state.orders.map((order) => <OrderView order={order}></OrderView>)}
            </div>
        );
    }
}

export default OrdersView;