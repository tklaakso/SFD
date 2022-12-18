import React from 'react';

import Card from 'react-bootstrap/Card';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

import NumericInput from 'react-numeric-input';

import isResponseOk from '../Utils.js';

import { MenuItem, MenuItemView } from './MenuView';

class Restaurant {
    constructor (props) {
        this.name = props.name;
        this.uuid = props.uuid;
    }
}

class RestaurantMenuView extends React.Component {
	constructor(props) {
		super(props);
        this.state = {
            restaurant: props.restaurant,
            modalItem: null,
            orderCount: 1,
        }
	}

    getMenu = () => {
        fetch("/restaurants/menu?id=" + this.state.restaurant.uuid, {
			credentials: "same-origin",
		})
        .then(isResponseOk)
		.then((data) => {
			this.setState({items: data.map((item) => new MenuItem(item))});
		})
		.catch((err) => {
			console.log(err);
			this.setState({items: []});
		});
    }

    onClickItem = (item) => {
        this.setState({modalItem: item});
    }

    handleModalClose = () => {
        this.setState({modalItem: null, orderCount: 1});
    }

    handleAddItem = () => {
        this.setState({modalItem: null, orderCount: 1});
    }

    onOrderCountChange = (value) => {
        this.setState({orderCount: Math.max(1, value)});
    }
    
    getPrice = () => {
        if (this.state.modalItem == null) {
            return 0;
        }
        return this.state.modalItem.price * this.state.orderCount;
    }

	render() {
        if (this.state.items == null) {
            this.getMenu();
            return <></>;
        }
        return (
            <div>
                <Modal size="fullscreen" show={this.state.modalItem != null} onHide={this.handleModalClose}>
                    <Modal.Header closeButton>
                        <Modal.Title>{this.state.modalItem?.name}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>{this.state.modalItem?.description}</p>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="secondary" onClick={this.handleModalClose}>Close</Button>
                        <NumericInput mobile className="form-control" precision={0} value={this.state.orderCount} onChange={this.onOrderCountChange}></NumericInput>
                        <Button variant="primary" onClick={this.handleAddItem}>Add (${this.getPrice().toFixed(2)})</Button>
                    </Modal.Footer>
                </Modal>
                {this.state.items.map((item) => <MenuItemView item={item} onClick={this.onClickItem} allowDeletion={false}></MenuItemView>)}
            </div>
        );
	}
}

class RestaurantView extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            restaurant: props.restaurant,
            onClick: props.onClick,
        }
    }

    onClick = () => {
        this.state.onClick(this.state.restaurant);
    }

    render() {
        return (
            <a style={{ cursor: "pointer" }} onClick={this.onClick}>
                <Card className="card-item" style={{ marginBottom: "10px", marginTop: "10px" }}>
                    <Card.Body>
                        <Card.Title>{this.state.restaurant.name}</Card.Title>
                    </Card.Body>
                </Card>
            </a>
        );
    }
}

class RestaurantBrowser extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            restaurants: null,
            viewingMenu: false,
            selectedRestaurant: null,
        };
    }

    getRestaurants = () => {
        fetch("/restaurants/browse/", {
            headers: {
                "Content-Type" : "application/json",
            },
            credentials: "same-origin",
        })
        .then(isResponseOk)
        .then((data) => {
            this.setState({restaurants: data.map((restaurant) => new Restaurant(restaurant))});
        })
        .catch((err) => {
            console.log(err);
        });
    }

    viewItems = (restaurant) => {
        this.setState({selectedRestaurant: restaurant, viewingMenu: true});
    }

    render() {
        if (this.state.viewingMenu) {
            return (
                <div>
                    <RestaurantMenuView restaurant={this.state.selectedRestaurant}></RestaurantMenuView>
                </div>
            );
        }
        if (this.state.restaurants == null) {
            this.getRestaurants();
            return <></>;
        }
        return (
            <div>
                {this.state.restaurants.map((restaurant) => <RestaurantView restaurant={restaurant} onClick={this.viewItems}></RestaurantView>)}
            </div>
        );
    }
}

export default RestaurantBrowser;