const mongoose = require('mongoose');
const Schema = mongoose.Schema;
//mongoose.set('debug', true);
const ClientsSchema = new Schema({
    name: String
});
const Client = mongoose.model('Client', ClientsSchema);

module.exports = Client;
