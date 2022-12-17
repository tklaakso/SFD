import React from 'react';

import Cookies from "universal-cookie";

import Card from 'react-bootstrap/Card'

import isResponseOk from '../Utils.js'

const cookies = new Cookies();

class MenuItemView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            name : props.name,
            description : props.description,
            price : props.price,
            uuid: props.uuid,
            onClick: props.onClick,
        };
    }

    onClick = () => {
        this.state.onClick({name: this.state.name, description: this.state.description, price: this.state.price, uuid: this.state.uuid});
    }

    render() {
        return (
            <a style={{ cursor: "pointer" }} onClick={this.onClick}>
                <Card className="card-item" style={{ marginBottom: "10px", marginTop: "10px" }}>
                    <Card.Body>
                        <Card.Title>{this.state.name}</Card.Title>
                        <Card.Text className="text-muted">{this.state.description}</Card.Text>
                    </Card.Body>
                </Card>
            </a>
        );
    }
}

class MenuBottomBar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            onAdd : props.onAdd,
        };
    }

    render() {
        return (
            <button type="submit" className="btn btn-primary" onClick={this.state.onAdd}>Add Item</button>
        );
    }
}

class MenuItemEditor extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            name : props.name,
            description : props.description,
            price : props.price,
            onSave : props.onSave,
        };
    }

    handleChange = (event) => {
        var stateObject = function() {
            var returnObj = {};
            returnObj[this.target.id] = this.target.value;
            return returnObj;
        }.bind(event)();
        this.setState(stateObject);
    }

    save = (event) => {
        event.preventDefault();
        this.state.onSave({name: this.state.name, description: this.state.description, price: this.state.price});
    }

    render() {
        return (
            <form onSubmit={this.save}>
                <div className="form-group">
                    <label htmlFor="name">Name</label>
                    <input type="text" className="form-control" id="name" name="name" value={this.state.name} onChange={this.handleChange} />
                </div>
                <div className="form-group">
                    <label htmlFor="description">Description</label>
                    <input type="text" className="form-control" id="description" name="description" value={this.state.description} onChange={this.handleChange} />
                </div>
                <div className="form-group">
                    <label htmlFor="price">Price</label>
                    <input type="number" className="form-control" id="price" name="price" value={this.state.price} onChange={this.handleChange} />
                </div>
                <button type="submit" className="btn btn-primary">Save</button>
            </form>
        );
    }
}

class MenuView extends React.Component {
	constructor(props) {
		super(props);
        this.state = {
            items: null,
            addingItem: false,
            modifiedItem: null,
        }
	}

    getMenu = () => {
        return fetch("/menus/view/", {
			headers: {
				"Content-Type" : "application/json",
			},
			credentials: "same-origin",
		})
        .then(isResponseOk)
		.then((data) => {
			this.setState({items: data});
		})
		.catch((err) => {
			console.log(err);
			this.setState({items: []});
		});
    }

    addItem = (item) => {
        fetch("/menus/add/", {
            method: "POST",
            headers: {
                "Content-Type" : "application/json",
                "X-CSRFToken" : cookies.get("csrftoken"),
            },
            credentials: "same-origin",
            body: JSON.stringify(item),
        })
        .then(isResponseOk)
        .then(() => {
            this.setState({addingItem: false, items: null});
            this.forceUpdate();
        })
        .catch((err) => {
            console.log(err);
        });
    }

    modifyItem = (item) => {
        fetch("/menus/modify/", {
            method: "POST",
            headers: {
                "Content-Type" : "application/json",
                "X-CSRFToken" : cookies.get("csrftoken"),
            },
            credentials: "same-origin",
            body: JSON.stringify({...item, ...{uuid: this.state.modifiedItem.uuid}}),
        })
        .then(isResponseOk)
        .then(() => {
            this.setState({addingItem: false, modifiedItem: null, items: null});
            this.forceUpdate();
        })
        .catch((err) => {
            console.log(err);
        });
    }

    onAddItem = () => {
        this.setState({addingItem: true});
        this.forceUpdate();
    }

    onSaveMenuItem = (item) => {
        if (this.state.modifiedItem == null) {
            this.addItem(item);
        }
        else {
            this.modifyItem(item);
        }
    }

    onModifyItem = (item) => {
        this.setState({addingItem: true, modifiedItem: item});
        this.forceUpdate();
    }
	
	render() {
        if (this.state.addingItem) {
            if (this.state.modifiedItem == null) {
                return (
                    <MenuItemEditor name="" description="" price={0} onSave={this.onSaveMenuItem}></MenuItemEditor>
                );
            }
            else {
                return (
                    <MenuItemEditor name={this.state.modifiedItem.name} description={this.state.modifiedItem.description} price={this.state.modifiedItem.price} onSave={this.onSaveMenuItem}></MenuItemEditor>
                );
            }
        }
        else {
            if (this.state.items == null) {
                this.getMenu().then(() => {this.forceUpdate()});
                return <></>;
            }
            return (
                <div>
                    {this.state.items.map((item) => <MenuItemView name={item.name} description={item.description} uuid={item.uuid} onClick={this.onModifyItem}></MenuItemView>)}
                    <MenuBottomBar onAdd={this.onAddItem}></MenuBottomBar>
                </div>
            );
        }
	}
}

export default MenuView;