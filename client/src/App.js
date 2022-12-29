import React from "react";
import Cookies from "universal-cookie";

import '@trendmicro/react-sidenav/dist/react-sidenav.css';
import NavigationBar from "./components/NavigationBar";
import MenuView from "./components/MenuView";
import RestaurantBrowser from "./components/RestaurantBrowser";
import CartView, { CartItem } from "./components/CartView";
import TopBar from "./components/TopBar";
import OrdersView from "./components/OrdersView";

import styled from 'styled-components';

import { isResponseOk, postJson, getJson } from './Utils';

import { Helmet } from "react-helmet";

const Main = styled.main`
    position: relative;
    overflow: hidden;
    transition: all .15s;
    padding: 0 20px;
    margin-left: ${props => (props.expanded ? 240 : 64)}px;
`;

const cookies = new Cookies();

class App extends React.Component {
	constructor(props) {
		super(props);

		this.navigationMode = "merchant";
		
		this.state = {
			username: "",
			password: "",
			error: "",
			isAuthenticated: false,
			sidebarExpanded: false,
			restaurant: null,
			cartViewOpen: false,
			cartItems: [],
		};
	}
	
	componentDidMount = () => {
		this.getSession();
	}
	
	getSession = () => {
		getJson("/accounts/session/")
		.then((data) => {
			console.log(data);
			if (data.isAuthenticated) {
				this.setState({isAuthenticated: true});
			} else {
				this.setState({isAuthenticated: false});
			}
		});
	}
	
	whoami = () => {
		getJson("/accounts/whoami/")
		.then((data) => {
			console.log("You are logged in as: " + data.username);
		});
	}

	handlePasswordChange = (event) => {
		this.setState({password : event.target.value});
	}

	handleUserNameChange = (event) => {
		this.setState({username : event.target.value});	
	}

	login = (event) => {
		event.preventDefault();
		postJson("/accounts/login/", {username : this.state.username, password : this.state.password},
		(err) => {
			this.setState({error: "Wrong username or password."});
		})
		.then((data) => {
			console.log(data);
			this.setState({isAuthenticated : true, username : "", password : "", error: ""});
		});
	}

	logout = () => {
		getJson("/accounts/logout/")
		.then((data) => {
			console.log(data);
			this.setState({isAuthenticated : false});
		});
	}

	onNavigationSelect = (selected) => {
		this.navigationMode = selected;
		this.forceUpdate();
	}

	onNavigationToggle = (expanded) => {
		this.setState({sidebarExpanded : expanded});
		this.forceUpdate();
	}

	makeRestaurant = (event) => {
		event.preventDefault();
		postJson("/restaurants/create/",
		{"name" : event.target.name.value,
		"address" : {
			"street_name" : event.target.street_name.value,
			"street_num" : event.target.street_num.value,
			"city" : event.target.city.value,
			"province" : event.target.province.value,
			"postal_code" : event.target.postal_code.value,
			"country" : "Canada",
		}})
		.then(() => {
			this.setState({restaurant: null});
			this.forceUpdate();
		});
	}

	getRestaurant = () => {
		return getJson("/restaurants/view/",
		() => {
			this.setState({restaurant: {}});
		})
		.then((data) => {
			if (data) {
				this.setState({restaurant: data});
			}
		});
	}

	renderMerchant = () => {
		if (this.state.restaurant == null) {
			this.getRestaurant().then(() => {this.forceUpdate()});
			return <></>;
		}
		if (Object.keys(this.state.restaurant).length === 0) {
			return (
				<div style={{position: "relative"}}>
					<form onSubmit={this.makeRestaurant}>
						<div className="form-group">
							<label htmlFor="Name">Restaurant Name</label>
							<input type="text" className="form-control" id="name" name="name" />
						</div>
						<div className="form-group">
							<label htmlFor="Street Name">Street Name</label>
							<input type="text" className="form-control" id="street_name" name="street_name" />
						</div>
						<div className="form-group">
							<label htmlFor="Street Number">Street Number</label>
							<input type="text" className="form-control" id="street_num" name="street_num" />
						</div>
						<div className="form-group">
							<label htmlFor="City">City</label>
							<input type="text" className="form-control" id="city" name="city" />
						</div>
						<div className="form-group">
							<label htmlFor="Province">Province</label>
							<input type="text" className="form-control" id="province" name="province" />
						</div>
						<div className="form-group">
							<label htmlFor="Postal Code">Postal Code</label>
							<input type="text" className="form-control" id="postal_code" name="postal_code" />
						</div>
						<button type="submit" className="btn btn-primary">Submit</button>
					</form>
				</div>
			);
		}
		else {
			return (
				<div style={{position: "relative"}}>
					<h1>{this.state.restaurant.name}</h1>
					<MenuView></MenuView>
				</div>
			);
		}
	}

	renderRestaurants = () => {
		return <RestaurantBrowser></RestaurantBrowser>;
	}

	renderOrders = () => {
		return <OrdersView></OrdersView>;
	}

	renderNavigatedPage = () => {
		switch (this.navigationMode) {
			case "merchant":
				return this.renderMerchant();
			case "restaurants":
				return this.renderRestaurants();
			case "orders":
				return this.renderOrders();
			default:
				return <></>;
		}
	}

	updateCartItems = () => {
		return getJson("/orders/cart/")
		.then((items) => {
			this.setState({cartItems : items.map((item) => new CartItem(item))});
		});
    }

	onViewCart = () => {
		this.updateCartItems().then(() => {this.setState({cartViewOpen: true})});
	}

	handleCartViewClose = () => {
		this.setState({cartViewOpen: false});
	}

	render() {
		if (!this.state.isAuthenticated) {
			return (
				<div className="container mt-3">
					<h1>React Cookie Auth</h1>
					<br />
					<h2>Login</h2>
					<form onSubmit={this.login}>
						<div className="form-group">
							<label htmlFor="username">Username</label>
							<input type="text" className="form-control" id="username" name="username" value={this.state.username} onChange={this.handleUserNameChange} />
						</div>
						<div className="form-group">
							<label htmlFor="username">Password</label>
							<input type="password" className="form-control" id="password" name="password" value={this.state.password} onChange={this.handlePasswordChange} />
							<div>
								{this.state.error &&
									<small className="text-danger">
										{this.state.error}
									</small>
								}
							</div>
						</div>
						<button type="submit" className="btn btn-primary">Login</button>
					</form>
				</div>
			);
		}
		return (
			<body>
				<TopBar onViewCart={this.onViewCart}></TopBar>
				<NavigationBar onSelect={this.onNavigationSelect} onToggle={this.onNavigationToggle} />
				<div style={{position: "relative"}}>
					<Helmet>
						<style>{"body { background-color: lightgray; }"}</style>
					</Helmet>
					<Main expanded={this.state.sidebarExpanded}>
						{this.renderNavigatedPage()}
					</Main>
				</div>
				<CartView open={this.state.cartViewOpen} items={this.state.cartItems} onClose={this.handleCartViewClose}></CartView>
			</body>
		);
	}
}

export default App;
