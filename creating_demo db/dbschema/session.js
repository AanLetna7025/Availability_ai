const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const SessionSchema = new Schema({
    session_name: String,
});
const Session = mongoose.model('Session', SessionSchema);
module.exports = Session;
