/*

Copyright 2008-2009 Thomas Paviot (thomas.paviot@free.fr)

This file is part of pythonOCC.

pythonOCC is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pythonOCC is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

*/
%{

// Headers necessary to define wrapped classes.

#include<GEOMImpl_ArcDriver.hxx>
#include<GEOMImpl_ArchimedeDriver.hxx>
#include<GEOMImpl_Block6Explorer.hxx>
#include<GEOMImpl_BlockDriver.hxx>
#include<GEOMImpl_BooleanDriver.hxx>
#include<GEOMImpl_BoxDriver.hxx>
#include<GEOMImpl_ChamferDriver.hxx>
#include<GEOMImpl_CircleDriver.hxx>
#include<GEOMImpl_ConeDriver.hxx>
#include<GEOMImpl_CopyDriver.hxx>
#include<GEOMImpl_CurveDriver.hxx>
#include<GEOMImpl_CylinderDriver.hxx>
#include<GEOMImpl_DraftDriver.hxx>
#include<GEOMImpl_EllipseDriver.hxx>
#include<GEOMImpl_ExportDriver.hxx>
#include<GEOMImpl_FaceDriver.hxx>
#include<GEOMImpl_FilletDriver.hxx>
#include<GEOMImpl_FillingDriver.hxx>
#include<GEOMImpl_Gen.hxx>
#include<GEOMImpl_GlueDriver.hxx>
#include<GEOMImpl_HealingDriver.hxx>
#include<GEOMImpl_I3DPrimOperations.hxx>
#include<GEOMImpl_IArc.hxx>
#include<GEOMImpl_IArchimede.hxx>
#include<GEOMImpl_IBasicOperations.hxx>
#include<GEOMImpl_IBlockTrsf.hxx>
#include<GEOMImpl_IBlocks.hxx>
#include<GEOMImpl_IBlocksOperations.hxx>
#include<GEOMImpl_IBoolean.hxx>
#include<GEOMImpl_IBooleanOperations.hxx>
#include<GEOMImpl_IBox.hxx>
#include<GEOMImpl_IChamfer.hxx>
#include<GEOMImpl_ICircle.hxx>
#include<GEOMImpl_ICone.hxx>
#include<GEOMImpl_ICopy.hxx>
#include<GEOMImpl_ICurve.hxx>
#include<GEOMImpl_ICurvesOperations.hxx>
#include<GEOMImpl_ICylinder.hxx>
#include<GEOMImpl_IDraft.hxx>
#include<GEOMImpl_IEllipse.hxx>
#include<GEOMImpl_IFace.hxx>
#include<GEOMImpl_IFillet.hxx>
#include<GEOMImpl_IFilling.hxx>
#include<GEOMImpl_IGlue.hxx>
#include<GEOMImpl_IGroupOperations.hxx>
#include<GEOMImpl_IHealing.hxx>
#include<GEOMImpl_IHealingOperations.hxx>
#include<GEOMImpl_IImportExport.hxx>
#include<GEOMImpl_IInsertOperations.hxx>
#include<GEOMImpl_ILine.hxx>
#include<GEOMImpl_ILocalOperations.hxx>
#include<GEOMImpl_IMarker.hxx>
#include<GEOMImpl_IMeasure.hxx>
#include<GEOMImpl_IMeasureOperations.hxx>
#include<GEOMImpl_IMirror.hxx>
#include<GEOMImpl_IOffset.hxx>
#include<GEOMImpl_IPartition.hxx>
#include<GEOMImpl_IPipe.hxx>
#include<GEOMImpl_IPipeBiNormal.hxx>
#include<GEOMImpl_IPipeDiffSect.hxx>
#include<GEOMImpl_IPipeShellSect.hxx>
#include<GEOMImpl_IPlane.hxx>
#include<GEOMImpl_IPlate.hxx>
#include<GEOMImpl_IPoint.hxx>
#include<GEOMImpl_IPolyline.hxx>
#include<GEOMImpl_IPosition.hxx>
#include<GEOMImpl_IPrism.hxx>
#include<GEOMImpl_IRevolution.hxx>
#include<GEOMImpl_IRotate.hxx>
#include<GEOMImpl_IScale.hxx>
#include<GEOMImpl_IShapes.hxx>
#include<GEOMImpl_IShapesOperations.hxx>
#include<GEOMImpl_ISketcher.hxx>
#include<GEOMImpl_ISphere.hxx>
#include<GEOMImpl_ISpline.hxx>
#include<GEOMImpl_IThickSolid.hxx>
#include<GEOMImpl_IThruSections.hxx>
#include<GEOMImpl_ITorus.hxx>
#include<GEOMImpl_ITransformOperations.hxx>
#include<GEOMImpl_ITranslate.hxx>
#include<GEOMImpl_IVariableFillet.hxx>
#include<GEOMImpl_IVector.hxx>
#include<GEOMImpl_ImportDriver.hxx>
#include<GEOMImpl_LineDriver.hxx>
#include<GEOMImpl_MarkerDriver.hxx>
#include<GEOMImpl_MeasureDriver.hxx>
#include<GEOMImpl_MirrorDriver.hxx>
#include<GEOMImpl_OffsetDriver.hxx>
#include<GEOMImpl_PartitionDriver.hxx>
#include<GEOMImpl_PipeDriver.hxx>
#include<GEOMImpl_PlaneDriver.hxx>
#include<GEOMImpl_PlateDriver.hxx>
#include<GEOMImpl_PointDriver.hxx>
#include<GEOMImpl_PolylineDriver.hxx>
#include<GEOMImpl_PositionDriver.hxx>
#include<GEOMImpl_PrismDriver.hxx>
#include<GEOMImpl_RevolutionDriver.hxx>
#include<GEOMImpl_RotateDriver.hxx>
#include<GEOMImpl_ScaleDriver.hxx>
#include<GEOMImpl_ShapeDriver.hxx>
#include<GEOMImpl_SketcherDriver.hxx>
#include<GEOMImpl_SphereDriver.hxx>
#include<GEOMImpl_SplineDriver.hxx>
#include<GEOMImpl_Template.hxx>
#include<GEOMImpl_ThickSolidDriver.hxx>
#include<GEOMImpl_ThruSectionsDriver.hxx>
#include<GEOMImpl_TorusDriver.hxx>
#include<GEOMImpl_TranslateDriver.hxx>
#include<GEOMImpl_Types.hxx>
#include<GEOMImpl_VariableFilletDriver.hxx>
#include<GEOMImpl_VectorDriver.hxx>

// Additional headers necessary for compilation.

#include<CDF.hxx>
#include<CDF_Application.hxx>
#include<CDF_Directory.hxx>
#include<CDF_DirectoryIterator.hxx>
#include<CDF_MetaDataDriver.hxx>
#include<CDF_MetaDataDriverError.hxx>
#include<CDF_MetaDataDriverFactory.hxx>
#include<CDF_RetrievableStatus.hxx>
#include<CDF_Session.hxx>
#include<CDF_Store.hxx>
#include<CDF_StoreList.hxx>
#include<CDF_StoreSetNameStatus.hxx>
#include<CDF_StoreStatus.hxx>
#include<CDF_SubComponentStatus.hxx>
#include<CDF_Timer.hxx>
#include<CDF_TryStoreStatus.hxx>
#include<CDF_TypeOfActivation.hxx>
#include<CDM_Application.hxx>
#include<CDM_COutMessageDriver.hxx>
#include<CDM_CanCloseStatus.hxx>
#include<CDM_DataMapIteratorOfMetaDataLookUpTable.hxx>
#include<CDM_DataMapIteratorOfNamesDirectory.hxx>
#include<CDM_DataMapIteratorOfPresentationDirectory.hxx>
#include<CDM_DataMapNodeOfMetaDataLookUpTable.hxx>
#include<CDM_DataMapNodeOfNamesDirectory.hxx>
#include<CDM_DataMapNodeOfPresentationDirectory.hxx>
#include<CDM_Document.hxx>
#include<CDM_DocumentHasher.hxx>
#include<CDM_DocumentPointer.hxx>
#include<CDM_ListIteratorOfListOfDocument.hxx>
#include<CDM_ListIteratorOfListOfReferences.hxx>
#include<CDM_ListNodeOfListOfDocument.hxx>
#include<CDM_ListNodeOfListOfReferences.hxx>
#include<CDM_ListOfDocument.hxx>
#include<CDM_ListOfReferences.hxx>
#include<CDM_MapIteratorOfMapOfDocument.hxx>
#include<CDM_MapOfDocument.hxx>
#include<CDM_MessageDriver.hxx>
#include<CDM_MetaData.hxx>
#include<CDM_MetaDataLookUpTable.hxx>
#include<CDM_NamesDirectory.hxx>
#include<CDM_NullMessageDriver.hxx>
#include<CDM_PresentationDirectory.hxx>
#include<CDM_Reference.hxx>
#include<CDM_ReferenceIterator.hxx>
#include<CDM_StackIteratorOfStackOfDocument.hxx>
#include<CDM_StackNodeOfStackOfDocument.hxx>
#include<CDM_StackOfDocument.hxx>
#include<CDM_StdMapNodeOfMapOfDocument.hxx>
#include<Handle_TCollection_AVLBaseNode.hxx>
#include<Handle_TCollection_HAsciiString.hxx>
#include<Handle_TCollection_HExtendedString.hxx>
#include<Handle_TCollection_MapNode.hxx>
#include<Handle_TCollection_SeqNode.hxx>
#include<TDF.hxx>
#include<TDF_Attribute.hxx>
#include<TDF_AttributeArray1.hxx>
#include<TDF_AttributeDataMap.hxx>
#include<TDF_AttributeDelta.hxx>
#include<TDF_AttributeDeltaList.hxx>
#include<TDF_AttributeDoubleMap.hxx>
#include<TDF_AttributeIndexedMap.hxx>
#include<TDF_AttributeIterator.hxx>
#include<TDF_AttributeList.hxx>
#include<TDF_AttributeMap.hxx>
#include<TDF_AttributeSequence.hxx>
#include<TDF_ChildIDIterator.hxx>
#include<TDF_ChildIterator.hxx>
#include<TDF_ClosureMode.hxx>
#include<TDF_ClosureTool.hxx>
#include<TDF_ComparisonTool.hxx>
#include<TDF_CopyLabel.hxx>
#include<TDF_CopyTool.hxx>
#include<TDF_Data.hxx>
#include<TDF_DataMapIteratorOfAttributeDataMap.hxx>
#include<TDF_DataMapIteratorOfLabelDataMap.hxx>
#include<TDF_DataMapIteratorOfLabelIntegerMap.hxx>
#include<TDF_DataMapIteratorOfLabelLabelMap.hxx>
#include<TDF_DataMapNodeOfAttributeDataMap.hxx>
#include<TDF_DataMapNodeOfLabelDataMap.hxx>
#include<TDF_DataMapNodeOfLabelIntegerMap.hxx>
#include<TDF_DataMapNodeOfLabelLabelMap.hxx>
#include<TDF_DataSet.hxx>
#include<TDF_DefaultDeltaOnModification.hxx>
#include<TDF_DefaultDeltaOnRemoval.hxx>
#include<TDF_Delta.hxx>
#include<TDF_DeltaList.hxx>
#include<TDF_DeltaOnAddition.hxx>
#include<TDF_DeltaOnForget.hxx>
#include<TDF_DeltaOnModification.hxx>
#include<TDF_DeltaOnRemoval.hxx>
#include<TDF_DeltaOnResume.hxx>
#include<TDF_DoubleMapIteratorOfAttributeDoubleMap.hxx>
#include<TDF_DoubleMapIteratorOfGUIDProgIDMap.hxx>
#include<TDF_DoubleMapIteratorOfLabelDoubleMap.hxx>
#include<TDF_DoubleMapNodeOfAttributeDoubleMap.hxx>
#include<TDF_DoubleMapNodeOfGUIDProgIDMap.hxx>
#include<TDF_DoubleMapNodeOfLabelDoubleMap.hxx>
#include<TDF_GUIDProgIDMap.hxx>
#include<TDF_HAllocator.hxx>
#include<TDF_HAttributeArray1.hxx>
#include<TDF_IDFilter.hxx>
#include<TDF_IDList.hxx>
#include<TDF_IDMap.hxx>
#include<TDF_IndexedMapNodeOfAttributeIndexedMap.hxx>
#include<TDF_IndexedMapNodeOfLabelIndexedMap.hxx>
#include<TDF_Label.hxx>
#include<TDF_LabelDataMap.hxx>
#include<TDF_LabelDoubleMap.hxx>
#include<TDF_LabelIndexedMap.hxx>
#include<TDF_LabelIntegerMap.hxx>
#include<TDF_LabelLabelMap.hxx>
#include<TDF_LabelList.hxx>
#include<TDF_LabelMap.hxx>
#include<TDF_LabelMapHasher.hxx>
#include<TDF_LabelNode.hxx>
#include<TDF_LabelNodePtr.hxx>
#include<TDF_LabelSequence.hxx>
#include<TDF_ListIteratorOfAttributeDeltaList.hxx>
#include<TDF_ListIteratorOfAttributeList.hxx>
#include<TDF_ListIteratorOfDeltaList.hxx>
#include<TDF_ListIteratorOfIDList.hxx>
#include<TDF_ListIteratorOfLabelList.hxx>
#include<TDF_ListNodeOfAttributeDeltaList.hxx>
#include<TDF_ListNodeOfAttributeList.hxx>
#include<TDF_ListNodeOfDeltaList.hxx>
#include<TDF_ListNodeOfIDList.hxx>
#include<TDF_ListNodeOfLabelList.hxx>
#include<TDF_MapIteratorOfAttributeMap.hxx>
#include<TDF_MapIteratorOfIDMap.hxx>
#include<TDF_MapIteratorOfLabelMap.hxx>
#include<TDF_Reference.hxx>
#include<TDF_RelocationTable.hxx>
#include<TDF_SequenceNodeOfAttributeSequence.hxx>
#include<TDF_SequenceNodeOfLabelSequence.hxx>
#include<TDF_StdMapNodeOfAttributeMap.hxx>
#include<TDF_StdMapNodeOfIDMap.hxx>
#include<TDF_StdMapNodeOfLabelMap.hxx>
#include<TDF_TagSource.hxx>
#include<TDF_Tool.hxx>
#include<TDF_Transaction.hxx>
#include<TDocStd.hxx>
#include<TDocStd_Application.hxx>
#include<TDocStd_ApplicationDelta.hxx>
#include<TDocStd_CompoundDelta.hxx>
#include<TDocStd_Context.hxx>
#include<TDocStd_DataMapIteratorOfLabelIDMapDataMap.hxx>
#include<TDocStd_DataMapNodeOfLabelIDMapDataMap.hxx>
#include<TDocStd_Document.hxx>
#include<TDocStd_LabelIDMapDataMap.hxx>
#include<TDocStd_Modified.hxx>
#include<TDocStd_MultiTransactionManager.hxx>
#include<TDocStd_Owner.hxx>
#include<TDocStd_PathParser.hxx>
#include<TDocStd_SequenceNodeOfSequenceOfApplicationDelta.hxx>
#include<TDocStd_SequenceNodeOfSequenceOfDocument.hxx>
#include<TDocStd_SequenceOfApplicationDelta.hxx>
#include<TDocStd_SequenceOfDocument.hxx>
#include<TDocStd_XLink.hxx>
#include<TDocStd_XLinkIterator.hxx>
#include<TDocStd_XLinkPtr.hxx>
#include<TDocStd_XLinkRoot.hxx>
#include<TDocStd_XLinkTool.hxx>

// Needed headers necessary for compilation.

%}
