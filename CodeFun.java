package cheng.jianfei.javafun;

import java.util.Arrays;
import java.util.function.Consumer;
import java.util.function.Function;

public class CodeFun {
	public static int[] plusOne(int[] digits) {
		int i = digits.length - 1;
		int sum = 0;
		while(i >= 0) {
			sum = digits[i] + 1;
			if(sum >= 10) {
				digits[i] = sum - 10;
				i--;
			} else {
				digits[i] = sum;
				i = -1;
			}
		}
		 
		int[] ret = digits;
		if(sum >= 10) {
			ret = new int[digits.length + 1];
			ret[0] = 1;
			System.arraycopy(digits, 0, ret, 1, digits.length);
		}
		
		return ret;
	}
	
    public static void findMissingInt(int[] nums) {
		if(nums == null || nums.length == 0)
			throw new IllegalArgumentException("input cannot be empty");
		
		int currentNum = nums[0];
		int count = 1;
		int numRepeats = 3;
		
		for(int i = 1; (i < nums.length) && (count <= numRepeats); i++) {
			if(currentNum == nums[i]) {
				count++;
			} else {
				if(count == numRepeats) {
					currentNum = nums[i];
					count=1;
				} else {
					break;
				}
			}
		}
		
		if(count > numRepeats) {
			System.out.println(currentNum + " occures " + count + " times more than the limit of " + numRepeats);
		} else if(count < numRepeats) {
			System.out.println(currentNum + " occures " + count + " times less than the expected " + numRepeats + " times");
		} else {
			System.out.println("Everything looks good");
		}
	}

    private static <T> void performTask1(Consumer<T> p, T arg){
    	try{
    		p.accept(arg);
    	}
    	catch(Exception e) {
    		System.out.println(e);
    	}
    }
    
    private static <T, R> R runFunction(Function<T, R> func, T arg) {
    	try{
    		return func.apply(arg);
    	}
    	catch(Exception e) {
    		System.out.println(e);
    		return null;
    	}
    }

    public static void main(String[] arguments) {
    	performTask1(CodeFun::findMissingInt, new int[]{});
    	performTask1(CodeFun::findMissingInt, null);
    	performTask1(CodeFun::findMissingInt, new int[]{1});
    	performTask1(CodeFun::findMissingInt, new int[]{1,1,1});
    	performTask1(CodeFun::findMissingInt, new int[]{1,1,1,2,2,3,3,3});
    	performTask1(CodeFun::findMissingInt, new int[]{1,1,1,2,2,2,2,3});
    	
    	System.out.println(Arrays.toString(runFunction(CodeFun::plusOne, new int[]{9, 9})));
    	System.out.println(Arrays.toString(runFunction(CodeFun::plusOne, new int[]{1, 9, 3})));
    	System.out.println(Arrays.toString(runFunction(CodeFun::plusOne, new int[]{1, 2, 3})));
    }
    
}
