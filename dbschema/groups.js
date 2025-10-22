const mongoose = require('mongoose')
const Schema = mongoose.Schema

const GroupSchema = new Schema({

    group_name: { type: String, default: "Group Name", index: true },

    group_description: { type: String, default: null },

    status: { type: String, enum: ['PROGRESS', 'COMPLETED'], require: true, default: 'PROGRESS' },

    project_id: { type: Schema.Types.ObjectId, ref: 'Project', require: true, index: true },

    milestone_id: { type: Schema.Types.ObjectId, ref: 'milestone', require: false, default: null, index: true },

    delete_status: { type: String, enum: ['0', '1'], require: true, default: '1' },
},
    { timestamps: true }
);

GroupSchema.methods.isDeleted = function () {
    return this.delete_status === '0';
};

const Group = mongoose.model('group', GroupSchema);
module.exports = Group;
