import React, { useState } from "react";
import axios from "axios";
import AsyncSelect from "react-select/async";
import { baseUrl } from "../../utils/constants/Constants";

const ProductOutModal = ({ setShowModal, addProduct }) => {
  const [productDetails, setProductDetails] = useState({
    id: null,
    productCode: "",
    name: "",
    brandName: "",
    categoryName: "",
    barcode: "",
    manufacturingDate: "",
    expiryDate: "",
    availableQuantity: 0,
    qty_requested: 0,
  });

  const loadProductOptions = async (inputValue) => {
    const response = await axios.get(`${baseUrl}store/products/?search=${inputValue}`);
    return response.data.results.map((product) => ({
      label: `${product.product_code} - ${product.name}`,
      value: product.id,
    }));
  };

  const handleProductChange = async (selectedOption) => {
    if (selectedOption) {
        const response = await axios.get(`${baseUrl}store/inventory/?search=${selectedOption.label}`);
        const inventory = response.data.results[0]; // Assuming the first result is the correct one

        setProductDetails({
            ...productDetails,
            id: selectedOption.value,
            productCode: inventory.product_code,
            name: inventory.name,
            brandName: inventory.brand_name,
            categoryName: inventory.category_name,
            barcode: inventory.barcode,
            manufacturingDate: inventory.manufacturing_date,
            expiryDate: inventory.expiry_date,
            availableQuantity: inventory.remaining_quantity,
        });
    }
  };

  const handleSaveProduct = () => {
    if (productDetails.qty_requested > productDetails.availableQuantity) {
      alert("Requested quantity exceeds available stock.");
      return;
    }
    addProduct(productDetails);
    setShowModal(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white w-full max-w-lg mx-auto p-6 rounded-lg">
        <h2 className="text-2xl font-bold mb-6">Add Product</h2>
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Product</label>
            <AsyncSelect
              loadOptions={loadProductOptions}
              onChange={handleProductChange}
              placeholder="Search Product Code or Name"
              className="mt-1 block w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Brand</label>
            <input
              type="text"
              value={productDetails.brandName}
              readOnly
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Category</label>
            <input
              type="text"
              value={productDetails.categoryName}
              readOnly
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Barcode</label>
            <input
              type="text"
              value={productDetails.barcode}
              readOnly
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Manufacturing Date</label>
            <input
              type="date"
              value={productDetails.manufacturingDate}
              readOnly
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Expiry Date</label>
            <input
              type="date"
              value={productDetails.expiryDate}
              readOnly
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Available Quantity</label>
            <input
              type="number"
              value={productDetails.availableQuantity}
              readOnly
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Requested Quantity</label>
            <input
              type="number"
              value={productDetails.qty_requested}
              onChange={(e) => setProductDetails({ ...productDetails, qty_requested: parseInt(e.target.value) })}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
        </div>
        <div className="mt-6 flex justify-end space-x-4">
          <button
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            onClick={() => setShowModal(false)}
          >
            Cancel
          </button>
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            onClick={handleSaveProduct}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductOutModal;
