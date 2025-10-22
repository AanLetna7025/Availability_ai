const mongoose = require('mongoose');
const Schema = mongoose.Schema;
//mongoose.set('debug', true);

const permissionSchema = new Schema({
    user_id: { type: mongoose.Schema.Types.ObjectId, ref: "User" },
    project_id: { type: mongoose.Schema.Types.ObjectId, ref: "Project" },
    assigned_by: { type: mongoose.Schema.Types.ObjectId, ref: "User" },
    permissions: [{
        action: String,
        allowed: Boolean
    }]
})
const Permission = mongoose.model('Permission', permissionSchema);

module.exports = Permission;
