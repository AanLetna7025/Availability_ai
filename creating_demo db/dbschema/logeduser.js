const mongoose = require('mongoose');
const Schema = mongoose.Schema;


const loggedUserSchema = new Schema({
    user_id: String,
    token: String,
    logged: Boolean
});

const LoggedUser = mongoose.model('LoggedUser', loggedUserSchema);

module.exports = LoggedUser;
