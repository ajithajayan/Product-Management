import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Select from 'react-select';
import AsyncSelect from 'react-select/async'; // Import AsyncSelect for dynamic loading
import { baseUrl } from '../../utils/constants/Constants';

const ProductForm = ({ fetchProducts, setShowModal }) => {
  const [productCode, setProductCode] = useState('');
  const [name, setName] = useState('');
  const [purchaseDate, setPurchaseDate] = useState('');
  const [quantity, setQuantity] = useState(0);
  const [expiryDate, setExpiryDate] = useState('');
  const [manufacturingDate, setManufacturingDate] = useState('');
  const [openingStock, setOpeningStock] = useState(0);

  const [selectedBrand, setSelectedBrand] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  const [selectedUnit, setSelectedUnit] = useState({ label: 'Pieces', value: 'pieces' });

  const [brands, setBrands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);

  const [isExistingProduct, setIsExistingProduct] = useState(false);

  useEffect(() => {
    fetchBrands();
    fetchCategories();
    fetchSuppliers();
  }, []);

  const fetchBrands = async () => {
    const response = await axios.get(baseUrl + 'store/brands/');
    setBrands(response.data.results.map(brand => ({ label: brand.name, value: brand.id })));
  };

  const fetchCategories = async () => {
    const response = await axios.get(baseUrl + 'store/categories/');
    setCategories(response.data.results.map(category => ({ label: category.name, value: category.id })));
  };

  const fetchSuppliers = async () => {
    const response = await axios.get(baseUrl + 'store/suppliers/');
    setSuppliers(response.data.results.map(supplier => ({ label: supplier.name, value: supplier.id })));
  };

  const loadProductCodes = async (inputValue) => {
    if (!inputValue) return [];
    const response = await axios.get(`${baseUrl}store/products/search_codes/?query=${inputValue}`);
    return response.data.map(product => ({ label: product.product_code, value: product.product_code }));
  };

  const handleProductCodeChange = async (selectedOption) => {
    if (!selectedOption) {
      resetFormFields();
      return;
    }

    const code = selectedOption.value;
    setProductCode(code);
    await checkProductCode(code);
  };

  const checkProductCode = async (code) => {
    try {
      const productResponse = await axios.get(`${baseUrl}store/products/${code}/`);
      if (productResponse.data) {
        setIsExistingProduct(true);
        setName(productResponse.data.name);
        setSelectedBrand({ label: productResponse.data.brand_name, value: productResponse.data.brand });
        setSelectedCategory({ label: productResponse.data.category_name, value: productResponse.data.category });
        setSelectedSupplier({ label: productResponse.data.supplier_name, value: productResponse.data.supplier });
        setSelectedUnit({ label: productResponse.data.unit_type, value: productResponse.data.unit_type });
        
        // Fetch total stock and set it as the opening stock
        const stockResponse = await axios.get(`${baseUrl}store/products/${code}/total_stock/`);
        setOpeningStock(stockResponse.data.total_stock);
      } else {
        resetFormFields();
      }
    } catch (error) {
      resetFormFields();
    }
  };

  const resetFormFields = () => {
    setIsExistingProduct(false);
    setName('');
    setSelectedBrand(null);
    setSelectedCategory(null);
    setSelectedSupplier(null);
    setSelectedUnit({ label: 'Pieces', value: 'pieces' });
    setOpeningStock(0);
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    const productData = {
      product_code: productCode || null, // Allow empty product code
      name,
      purchase_date: purchaseDate,
      unit: selectedUnit.value,
      quantity,
      expiry_date: expiryDate,
      manufacturing_date: manufacturingDate,
      brand: selectedBrand?.value,
      category: selectedCategory?.value,
      supplier: selectedSupplier?.value,
      opening_stock: openingStock + quantity, // Add the quantity to opening stock for total stock
    };

    try {
      if (isExistingProduct) {
        await axios.post(`${baseUrl}store/products/${productCode}/add_stock/`, productData);
      } else {
        await axios.post(baseUrl + 'store/products/', productData);
      }
      fetchProducts();
      setShowModal(false);
    } catch (error) {
      console.error('Error saving product:', error);
    }
  };

  // Unit options
  const unitOptions = [
    { label: 'Pieces', value: 'pieces' },
    { label: 'Kilograms', value: 'kilograms' },
    { label: 'Liters', value: 'liters' },
    { label: 'Meters', value: 'meters' },
    { label: 'Pounds', value: 'pounds' },
    // Add more unit options as needed
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="relative bg-white w-full max-w-3xl mx-4 md:mx-0 md:w-3/4 lg:w-2/3 xl:w-1/2 shadow-lg rounded-lg overflow-hidden mt-20">
        <button
          className="absolute top-3 right-3 text-gray-600 hover:text-gray-900"
          onClick={() => setShowModal(false)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="p-6">
          <h2 className="text-2xl font-bold mb-6 text-center">Create Product / Add Stock</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700">Product Code (Optional)</label>
                <AsyncSelect
                  loadOptions={loadProductCodes}
                  onChange={handleProductCodeChange}
                  isClearable
                  placeholder="Type to search..."
                  className="mt-1 block w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Product Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                  readOnly={isExistingProduct}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Purchase Date</label>
                <input
                  type="date"
                  value={purchaseDate}
                  onChange={(e) => setPurchaseDate(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Unit</label>
                <Select
                  value={selectedUnit}
                  onChange={setSelectedUnit}
                  options={unitOptions}
                  className="mt-1 block w-full"
                  isSearchable
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Quantity</label>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Expiry Date</label>
                <input
                  type="date"
                  value={expiryDate}
                  onChange={(e) => setExpiryDate(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Manufacturing Date</label>
                <input
                  type="date"
                  value={manufacturingDate}
                  onChange={(e) => setManufacturingDate(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Opening Stock</label>
                <input
                  type="number"
                  value={openingStock}
                  onChange={(e) => setOpeningStock(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Brand</label>
                <Select
                  value={selectedBrand}
                  onChange={setSelectedBrand}
                  options={brands}
                  className="mt-1 block w-full"
                  isSearchable
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Category</label>
                <Select
                  value={selectedCategory}
                  onChange={setSelectedCategory}
                  options={categories}
                  className="mt-1 block w-full"
                  isSearchable
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Supplier</label>
                <Select
                  value={selectedSupplier}
                  onChange={setSelectedSupplier}
                  options={suppliers}
                  className="mt-1 block w-full"
                  isSearchable
                />
              </div>
            </div>
            <div className="text-center">
              <button
                type="submit"
                className="inline-flex justify-center px-4 py-2 text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700"
              >
                {isExistingProduct ? 'Add Stock' : 'Create Product'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProductForm;
