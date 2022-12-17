import React from 'react';

import SideNav, { Toggle, Nav, NavItem, NavIcon, NavText } from '@trendmicro/react-sidenav';

import restaurant from "./restaurant.png";
import fork from "./fork.png";
import car from "./car.png";

class NavigationBar extends React.Component {
	constructor(props) {
		super(props);
		this.onSelect = props.onSelect;
		this.onToggle = props.onToggle;
	}
	
	render() {
		return (
			<SideNav onSelect={this.onSelect} onToggle={this.onToggle}>
				<Toggle />
				<Nav defaultSelected="merchant">
					<NavItem eventKey="merchant">
						<NavIcon>
							<img src={restaurant} width="24px" height="24px"></img>
						</NavIcon>
						<NavText>
							Merchant
						</NavText>
					</NavItem>
					<NavItem eventKey="restaurants">
						<NavIcon>
							<img src={fork} width="24px" height="24px"></img>
						</NavIcon>
						<NavText>
							Restaurants
						</NavText>
					</NavItem>
					<NavItem eventKey="orders">
						<NavIcon>
							<img src={car} width="24px" height="24px"></img>
						</NavIcon>
						<NavText>
							Orders
						</NavText>
					</NavItem>
				</Nav>
			</SideNav>
			);
	}
}

export default NavigationBar;