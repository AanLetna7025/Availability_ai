const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const InviteUserSchema = new Schema({
    user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    project_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Project' },
    status: { type: String, enum: ['active', 'deleted'], require: true, default: 'active' },
    isadmin: { type: Boolean, default: false }
});
const InviteUser = mongoose.model('invite_users', InviteUserSchema);
module.exports = InviteUser;
