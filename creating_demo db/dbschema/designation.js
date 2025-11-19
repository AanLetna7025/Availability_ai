const mongoose = require('mongoose');
const Schema = mongoose.Schema;
//mongoose.set('debug', true);
const DesignationSchema = new Schema({
    name: String,
    developerstatus: Boolean
}, {
    toJSON: { virtuals: true }, // So `res.json()` and other `JSON.stringify()` functions include virtuals
    toObject: { virtuals: true } // So `console.log()` and other functions that use `toObject()` include virtuals
});



DesignationSchema.virtual('users', {
    ref: 'User',
    localField: '_id',
    foreignField: 'designation'
});

const Designation = mongoose.model('Designation', DesignationSchema);

module.exports = Designation;
