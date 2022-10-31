import React from 'react';

import SideNav, { Toggle, Nav, NavItem, NavIcon, NavText } from '@trendmicro/react-sidenav';

class NavigationBar extends React.Component {
	constructor(props) {
		super(props);
	}
	
	render() {
		return (
			<SideNav onSelect={(selected) => {
				
				}}
			>
				<Toggle />
				<Nav defaultSelected="restaurants">
					<NavItem eventKey="restaurants">
						<NavText>
							Restaurants
						</NavText>
					</NavItem>
				</Nav>
			</SideNav>
			);
	}
}

export default NavigationBar;