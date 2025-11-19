const mongoose = require('mongoose');
const Schema = mongoose.Schema;
//mongoose.set('debug', true);
// const Permission = require('../models/permission')

const RolesSchema = new Schema({
    name: String,
    status: String,
    permissions: [{
        action: String,
        allowed: Boolean
    }],
});
const Role = mongoose.model('Role', RolesSchema);

module.exports = Role;
