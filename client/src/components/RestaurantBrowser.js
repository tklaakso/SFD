import React from 'react';

import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';

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
        }
	}

    getMenu = () => {
        return fetch("/restaurants/menu?id=" + this.state.restaurant.uuid, {
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

    onClickItem = () => {

    }
	
	render() {
        if (this.state.items == null) {
            this.getMenu().then(() => {this.forceUpdate()});
            return <></>;
        }
        return (
            <div>
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
        return fetch("/restaurants/browse/", {
            headers: {
                "Content-Type" : "application/json",
            },
            credentials: "same-origin",
        })
        .then(isResponseOk)
        .then((data) => {
            this.setState({restaurants: data.map((restaurant) => new Restaurant(restaurant))});
            this.forceUpdate();
        })
        .catch((err) => {
            console.log(err);
        });
    }

    viewItems = (restaurant) => {
        this.setState({selectedRestaurant: restaurant, viewingMenu: true});
        this.forceUpdate();
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
            this.getRestaurants().then(() => {this.forceUpdate()});
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