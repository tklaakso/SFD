import React from 'react';

import Cookies from "universal-cookie";

import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';

import isResponseOk from '../Utils.js';

const cookies = new Cookies();

export class MenuItem {
    constructor(props) {
        this.name = props.name;
        this.description = props.description;
        this.price = props.price;
        this.uuid = props.uuid;
    }

    stringifyProperties = () => {
        return JSON.stringify({name: this.name, description: this.description, price: this.price});
    }

    stringifyFull = () => {
        return JSON.stringify({name: this.name, description: this.description, price: this.price, uuid: this.uuid});
    }
}

export class MenuItemView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            item: props.item,
            onClick: props.onClick,
            onDeleteClick: props.onDeleteClick,
            allowDeletion: props.allowDeletion,
        };
    }

    onClick = () => {
        this.state.onClick(this.state.item);
    }

    onDeleteClick = (event) => {
        event.stopPropagation();
        this.state.onDeleteClick(this.state.item);
    }

    render() {
        return (
            <a style={{ cursor: "pointer" }} onClick={this.onClick}>
                <Card className="card-item" style={{ marginBottom: "10px", marginTop: "10px" }}>
                    <Card.Body>
                        <Card.Title>{this.state.item.name}</Card.Title>
                        <Card.Text className="text-muted">{this.state.item.description}</Card.Text>
                        {this.state.allowDeletion && <Button style={{ position: "absolute", right: "30px", top: "50%", transform: "translateY(-50%)" }} variant="danger" onClick={this.onDeleteClick}>Delete</Button>}
                    </Card.Body>
                </Card>
            </a>
        );
    }
}

export class MenuBottomBar extends React.Component {
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

export class MenuItemEditor extends React.Component {
    constructor(props) {
        super(props);
        if (props.item == null) {
            this.state = {
                name: "",
                description: "",
                price: 0,
                uuid: null,
                onSave: props.onSave,
            };
        }
        else {
            this.state = {
                name: props.item.name,
                description: props.item.description,
                price: props.item.price,
                uuid: props.item.uuid,
                onSave: props.onSave,
            };
        }
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
        this.state.onSave(new MenuItem({name: this.state.name, description: this.state.description, price: this.state.price, uuid: this.state.uuid}));
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
			this.setState({items: data.map((item) => new MenuItem(item))});
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
            body: item.stringifyProperties(),
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
            body: item.stringifyFull(),
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

    deleteItem = (item) => {
        fetch("/menus/remove/", {
            method: "POST",
            headers: {
                "Content-Type" : "application/json",
                "X-CSRFToken" : cookies.get("csrftoken"),
            },
            credentials: "same-origin",
            body: JSON.stringify({uuid: item.uuid}),
        })
        .then(isResponseOk)
        .then(() => {
            this.setState({items: null});
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
            return (
                <MenuItemEditor item={this.state.modifiedItem} onSave={this.onSaveMenuItem}></MenuItemEditor>
            );
        }
        else {
            if (this.state.items == null) {
                this.getMenu().then(() => {this.forceUpdate()});
                return <></>;
            }
            return (
                <div>
                    {this.state.items.map((item) => <MenuItemView item={item} onClick={this.onModifyItem} onDeleteClick={this.deleteItem} allowDeletion={true}></MenuItemView>)}
                    <MenuBottomBar onAdd={this.onAddItem}></MenuBottomBar>
                </div>
            );
        }
	}
}

export default MenuView;