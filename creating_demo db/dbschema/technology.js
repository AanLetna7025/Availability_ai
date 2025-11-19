const mongoose = require('mongoose');
const Schema = mongoose.Schema;
//mongoose.set('debug', true);
const TechnologiesSchema = new Schema({
    name: String,
    type:{type: String,enum : ['client','server'],require:true},
    status:String
});
const Technology = mongoose.model('Technology', TechnologiesSchema);

module.exports = Technology;
