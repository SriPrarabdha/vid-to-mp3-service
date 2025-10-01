import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import uuid


@dataclass
class TestUser:
    user_name: str
    password: str
    email: Optional[str] = None


class AuthAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.register_endpoint = f"{self.base_url}/auth/register"
    
    async def test_single_user_registration(self, 
                                          user_name: str = None, 
                                          password: str = "testpass123",
                                          email: str = None) -> Dict:
        """
        Test registration with a single user
        
        Args:
            user_name: Username (will generate random if None)
            password: Password for the user
            email: Email (will generate random if None)
            
        Returns:
            Dictionary with test results
        """
        # Generate random user data if not provided
        if user_name is None:
            user_name = f"testuser_{uuid.uuid4().hex[:8]}"
        if email is None:
            email = f"{user_name}@test.com"
        
        test_user = TestUser(
            user_name=user_name,
            password=password,
            email=email
        )
        
        print(f"🧪 Testing single user registration...")
        print(f"   Username: {test_user.user_name}")
        print(f"   Email: {test_user.email}")
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "user_name": test_user.user_name,
                    "password": test_user.password,
                    "email": test_user.email
                }
                
                async with session.post(
                    self.register_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    response_time = time.time() - start_time
                    status_code = response.status
                    
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
                    
                    result = {
                        "success": status_code == 200,
                        "status_code": status_code,
                        "response_time": round(response_time * 1000, 2),  # in ms
                        "response_data": response_data,
                        "test_user": {
                            "user_name": test_user.user_name,
                            "email": test_user.email
                        }
                    }
                    
                    # Print results
                    if result["success"]:
                        print(f"✅ Registration successful!")
                        print(f"   Response time: {result['response_time']}ms")
                        print(f"   User ID: {response_data.get('id', 'N/A')}")
                    else:
                        print(f"❌ Registration failed!")
                        print(f"   Status code: {status_code}")
                        print(f"   Error: {response_data}")
                    
                    return result
                    
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": str(e),
                    "response_time": round((time.time() - start_time) * 1000, 2),
                    "test_user": {
                        "user_name": test_user.user_name,
                        "email": test_user.email
                    }
                }
                print(f"❌ Request failed: {e}")
                return error_result

    async def _register_single_concurrent_user(self, session: aiohttp.ClientSession, user_index: int) -> Dict:
        """Helper function to register a single user (used for concurrent testing)"""
        user_name = f"concurrent_user_{user_index}_{uuid.uuid4().hex[:6]}"
        # user_name = "manas"
        email = f"{user_name}@test.com"
        
        payload = {
            "user_name": user_name,
            "password": "concurrenttest123",
            "email": email
        }
        
        start_time = time.time()
        
        try:
            async with session.post(
                self.register_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                response_time = time.time() - start_time
                status_code = response.status
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "user_index": user_index,
                    "success": status_code == 200,
                    "status_code": status_code,
                    "response_time": round(response_time * 1000, 2),
                    "response_data": response_data,
                    "user_name": user_name,
                    "email": email
                }
                
        except Exception as e:
            return {
                "user_index": user_index,
                "success": False,
                "error": str(e),
                "response_time": round((time.time() - start_time) * 1000, 2),
                "user_name": user_name,
                "email": email
            }

    async def test_concurrent_user_registration(self, num_users: int = 10) -> Dict:
        """
        Test concurrent user registration
        
        Args:
            num_users: Number of concurrent users to simulate
            
        Returns:
            Dictionary with aggregated test results
        """
        print(f"🚀 Testing {num_users} concurrent user registrations...")
        
        start_time = time.time()
        
        # Create a single session for all requests
        connector = aiohttp.TCPConnector(limit=num_users + 5)  # Allow enough connections
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Create tasks for concurrent requests
            tasks = [
                self._register_single_concurrent_user(session, i) 
                for i in range(num_users)
            ]
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_time = time.time() - start_time
            
            # Process results
            successful_registrations = []
            failed_registrations = []
            errors = []
            
            for result in results:
                if isinstance(result, Exception):
                    errors.append(str(result))
                elif result.get("success", False):
                    successful_registrations.append(result)
                else:
                    failed_registrations.append(result)
            
            # Calculate statistics
            response_times = [r["response_time"] for r in successful_registrations + failed_registrations 
                            if "response_time" in r]
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            success_rate = (len(successful_registrations) / num_users) * 100
            
            # Compile final results
            final_results = {
                "total_users": num_users,
                "successful_registrations": len(successful_registrations),
                "failed_registrations": len(failed_registrations),
                "errors": len(errors),
                "success_rate": round(success_rate, 2),
                "total_test_time": round(total_time * 1000, 2),  # in ms
                "avg_response_time": round(avg_response_time, 2),
                "min_response_time": round(min_response_time, 2),
                "max_response_time": round(max_response_time, 2),
                "requests_per_second": round(num_users / total_time, 2),
                "detailed_results": {
                    "successful": successful_registrations,
                    "failed": failed_registrations,
                    "errors": errors
                }
            }
            
            # Print summary
            print(f"\n📊 Concurrent Testing Results:")
            print(f"   Total users: {final_results['total_users']}")
            print(f"   Successful: {final_results['successful_registrations']} ({final_results['success_rate']}%)")
            print(f"   Failed: {final_results['failed_registrations']}")
            print(f"   Errors: {final_results['errors']}")
            print(f"   Total time: {final_results['total_test_time']}ms")
            print(f"   Avg response time: {final_results['avg_response_time']}ms")
            print(f"   Min response time: {final_results['min_response_time']}ms")
            print(f"   Max response time: {final_results['max_response_time']}ms")
            print(f"   Requests/second: {final_results['requests_per_second']}")
            
            # Show some failed requests if any
            if failed_registrations:
                print(f"\n⚠️ First few failures:")
                for failure in failed_registrations[:3]:
                    print(f"   User {failure['user_index']}: {failure.get('error', 'HTTP ' + str(failure['status_code']))}")
            
            return final_results


async def main():
    """Example usage of the testing functions"""
    # Initialize the tester
    tester = AuthAPITester(base_url="http://localhost:8000")  # Adjust URL as needed
    
    print("🔥 Starting Auth API Tests\n")
    
    # Test 1: Single user registration
    print("=" * 50)
    single_user_result = await tester.test_single_user_registration()
    
    print("\n" + "=" * 50)
    
    # Test 2: Concurrent user registration
    concurrent_result = await tester.test_concurrent_user_registration(num_users=10)
    
    print(f"\n🏁 All tests completed!")
    
    # Optionally return results for further processing
    return {
        "single_user": single_user_result,
        "concurrent": concurrent_result
    }


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())
    
    # Optionally save results to file
    with open("auth_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to 'auth_test_results.json'")