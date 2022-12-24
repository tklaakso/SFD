import React from 'react';

import Cookies from "universal-cookie";

import Card from 'react-bootstrap/Card';
import CloseButton from 'react-bootstrap/CloseButton';

import { isResponseOk, postJson, getJson } from '../Utils';

const cookies = new Cookies();

export class MenuItem {
    constructor(props) {
        this.name = props.name;
        this.description = props.description;
        this.price = props.price;
        this.uuid = props.uuid;
    }

    getProperties = () => {
        return {name: this.name, description: this.description, price: this.price};
    }

    getFull = () => {
        return {name: this.name, description: this.description, price: this.price, uuid: this.uuid};
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
                        {this.state.allowDeletion && <CloseButton style={{ position: "absolute", right: "30px", top: "50%", transform: "translateY(-50%)" }} onClick={this.onDeleteClick}></CloseButton>}
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
        getJson("/menus/view/",
        () => {
            this.setState({items: []});
        })
        .then((data) => {
            this.setState({items: data.map((item) => new MenuItem(item))});
        });
    }

    addItem = (item) => {
        postJson("/menus/add/", item.getProperties())
        .then(() => {
            this.setState({addingItem: false, items: null});
        });
    }

    modifyItem = (item) => {
        postJson("/menus/modify/", item.getFull())
        .then(() => {
            this.setState({addingItem: false, modifiedItem: null, items: null});
        });
    }

    deleteItem = (item) => {
        postJson("/menus/remove/", {uuid: item.uuid})
        .then(() => {
            this.setState({items: null});
        });
    }


    onAddItem = () => {
        this.setState({addingItem: true});
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
    }
	
	render() {
        if (this.state.addingItem) {
            return (
                <MenuItemEditor item={this.state.modifiedItem} onSave={this.onSaveMenuItem}></MenuItemEditor>
            );
        }
        else {
            if (this.state.items == null) {
                this.getMenu();
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