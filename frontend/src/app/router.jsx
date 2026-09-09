import {createBrowserRouter} from 'react-router-dom';
import Home from '../pages/Home'; import EstablishmentDetails from '../pages/EstablishmentDetails'; import Review from '../pages/Review'; import ReviewResult from '../pages/ReviewResult'; import InternalReviews from '../pages/InternalReviews';
export default createBrowserRouter([{path:'/',element:<Home/>},{path:'/establishments/:id',element:<EstablishmentDetails/>},{path:'/review/:token',element:<Review/>},{path:'/review/:token/result',element:<ReviewResult/>},{path:'/internal/reviews',element:<InternalReviews/>}]);

