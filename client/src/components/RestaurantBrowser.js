import React from 'react';

import Cookies from 'universal-cookie';

import Card from 'react-bootstrap/Card';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import NumericInput from 'react-numeric-input';

import { isResponseOk, postJson, getJson } from '../Utils';

import { MenuItem, MenuItemView } from './MenuView';

import Autocomplete from 'react-google-autocomplete';

const cookies = new Cookies();

export class Address {
    constructor (props) {
        this.street_num = props.street_num;
        this.street_name = props.street_name;
        this.postal_code = props.postal_code;
        this.city = props.city;
        this.province = props.province;
        this.country = props.country;
        this.unit = props.unit;
    }

    toString() {
        var res = this.street_num + " " + this.street_name + ", " + this.city + ", " + this.province + ", " + this.country + ", " + this.postal_code;
        if (this.unit) {
            res += ", " + this.unit;
        }
        return res;
    }
}

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
            showModal: false,
            orderCount: 1,
        }
	}

    getMenu = () => {
        getJson("/restaurants/menu?id=" + this.state.restaurant.uuid,
        (err) => {
            this.setState({items: []});
        })
        .then((data) => {
            this.setState({items: data.map((item) => new MenuItem(item))});
        })
    }

    addItem = (item, quantity) => {
        postJson("/orders/add/", {'item' : item.uuid, 'quantity' : quantity})
        .then(() => {
            this.setState({showModal: false});
        });
    }

    onClickItem = (item) => {
        this.setState({modalItem: item, orderCount: 1, showModal: true});
    }

    handleModalClose = () => {
        this.setState({showModal: false});
    }

    handleAddItem = () => {
        this.addItem(this.state.modalItem, this.state.orderCount);
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
                <Modal size="lg" show={this.state.showModal} onHide={this.handleModalClose}>
                    <Modal.Header closeButton>
                        <Modal.Title>{this.state.modalItem?.name}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>{this.state.modalItem?.description}</p>
                    </Modal.Body>
                    <Modal.Footer>
                        <Container>
                            <Row>
                                <Col><Button variant="secondary" onClick={this.handleModalClose}>Close</Button></Col>
                                <Col><NumericInput mobile className="form-control" precision={0} value={this.state.orderCount} onChange={this.onOrderCountChange}></NumericInput></Col>
                                <Col><Button className="float-end" variant="primary" onClick={this.handleAddItem}>Add (${this.getPrice().toFixed(2)})</Button></Col>
                            </Row>
                        </Container>
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
            address: null,
            fetchedAddress: false,
        };
    }

    getRestaurants = () => {
        postJson("/restaurants/browse/", this.state.address)
        .then((data) => {
            this.setState({restaurants: data.map((restaurant) => new Restaurant(restaurant))});
        });
    }

    getAddress = () => {
        getJson("/geo/address/",
        () => {
            this.setState({fetchedAddress: true});
        })
        .then((data) => {
            this.setState({fetchedAddress: true, address: new Address(data)});
        });
    }

    viewItems = (restaurant) => {
        this.setState({selectedRestaurant: restaurant, viewingMenu: true});
    }

    registerAddress = (data) => {
        var addr_props = {};
        var entries = data.address_components.values();
        for (let component of entries) {
            var type = component.types[0];
            switch (type) {
                case "street_number":
                    addr_props.street_num = parseInt(component.long_name);
                    break;
                case "route":
                    addr_props.street_name = component.long_name;
                    break;
                case "postal_code":
                    addr_props.postal_code = component.long_name;
                    break;
                case "locality":
                    addr_props.city = component.long_name;
                    break;
                case "administrative_area_level_1":
                    addr_props.province = component.long_name;
                    break;
                case "country":
                    addr_props.country = component.long_name;
                    break;
            }
        }
        this.setState({restaurants: null, address: new Address(addr_props)});
    }

    render() {
        if (this.state.viewingMenu) {
            return (
                <div>
                    <RestaurantMenuView restaurant={this.state.selectedRestaurant}></RestaurantMenuView>
                </div>
            );
        }
        if (this.state.restaurants == null && this.state.address != null) {
            this.getRestaurants();
        }
        if (this.state.address == null && !this.state.fetchedAddress) {
            this.getAddress();
        }
        return (
            <div>
                <div>
                    <div className="flex-center" style={{marginTop: "30px"}}>
                        <h2>Where you at?</h2>
                    </div>
                    <div className="flex-center">
                        <Autocomplete placeholder="Where should we deliver?" style={{textAlign: "center", "border-radius": "25px", width: "500px", height: "50px", padding: "0 20px"}} options={{types: ["address"]}} apiKey="AIzaSyB-yNql09AeAYM2ys8QYv1RxpUdJFPxgrI" onPlaceSelected={this.registerAddress}></Autocomplete>
                    </div>
                    {this.state.address != null && <div className="flex-center">
                        <p>Delivering to {this.state.address.toString()}</p>
                    </div>}
                </div>
                {this.state.restaurants != null && this.state.restaurants.map((restaurant) => <RestaurantView restaurant={restaurant} onClick={this.viewItems}></RestaurantView>)}
            </div>
        );
    }
}

export default RestaurantBrowser;