const mongoose = require('mongoose')
const projectDocumentSchema = mongoose.Schema({
    project_id: { type: mongoose.Types.ObjectId, required: true, ref: 'Project' },
    documentName:{type:String,default:null},
    description: { type: String, default: null },
    documentOriginalName: { type: String, default: null },
    documentUniqueName: { type: String, required:true },
    s3Key:{type:String,required:true },
    s3Url: { type: String, required:true  },
    documentType: { type: String, default: null }
}, {
    timestamps: true
})
module.exports = mongoose.model('project_documents', projectDocumentSchema);
